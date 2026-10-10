import sys
import time
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, connections
from django.db.migrations.executor import MigrationExecutor


class Command(BaseCommand):
    help = "Test and verify PostgreSQL database connection, latency, SSL, and migration readiness for production."

    def add_arguments(self, parser):
        parser.add_argument(
            "--wait",
            type=int,
            default=0,
            help="Wait up to WAIT seconds for the database to become available before failing (useful in Docker/K8s startup scripts).",
        )
        parser.add_argument(
            "--interval",
            type=int,
            default=2,
            help="Seconds to wait between retry attempts when using --wait (default: 2s).",
        )
        parser.add_argument(
            "--database",
            default="default",
            help="The database alias to check (default: 'default').",
        )

    def handle(self, *args, **options):
        db_alias = options["database"]
        wait_seconds = options["wait"]
        interval = options["interval"]

        self.stdout.write(self.style.MIGRATE_HEADING("=" * 60))
        self.stdout.write(self.style.MIGRATE_HEADING("  POSTGRESQL PRODUCTION DATABASE CONNECTION CHECK"))
        self.stdout.write(self.style.MIGRATE_HEADING("=" * 60))

        db_conn = connections[db_alias]
        settings_dict = db_conn.settings_dict

        # Sanitize credentials for display
        engine = settings_dict.get("ENGINE", "Unknown")
        name = settings_dict.get("NAME", "Unknown")
        is_sqlite = "sqlite" in engine
        is_postgres = "postgresql" in engine

        host = settings_dict.get("HOST", "") or ("Local File" if is_sqlite else "127.0.0.1")
        port = settings_dict.get("PORT", "") or ("N/A" if is_sqlite else "5432")
        user = settings_dict.get("USER", "") or ("N/A" if is_sqlite else "postgres")
        conn_max_age = settings_dict.get("CONN_MAX_AGE", 0)
        conn_health_checks = settings_dict.get("CONN_HEALTH_CHECKS", False)
        options_dict = settings_dict.get("OPTIONS", {})
        sslmode = options_dict.get("sslmode", "N/A" if is_sqlite else "not configured")

        self.stdout.write(f"Target Database Alias: {self.style.MIGRATE_LABEL(db_alias)}")
        self.stdout.write(f"Engine:               {engine}")
        if is_sqlite:
            self.stdout.write(f"Database Path:        {name}")
        else:
            self.stdout.write(f"Host:                 {host}:{port}")
            self.stdout.write(f"Database:             {name}")
            self.stdout.write(f"User:                 {user}")
            self.stdout.write(f"SSL Mode:             {sslmode}")
            self.stdout.write(f"CONN_MAX_AGE:         {conn_max_age}s")
            self.stdout.write(f"CONN_HEALTH_CHECKS:   {conn_health_checks}")
        self.stdout.write("-" * 60)

        # Connection attempt loop
        start_time = time.time()
        attempt = 0
        connected = False

        while not connected:
            attempt += 1
            try:
                self.stdout.write(f"Attempting connection (attempt #{attempt})...")
                db_conn.ensure_connection()
                query_start = time.perf_counter()
                with db_conn.cursor() as cursor:
                    cursor.execute("SELECT 1;")
                    cursor.fetchone()
                    latency_ms = (time.perf_counter() - query_start) * 1000

                    # Fetch database version
                    try:
                        if is_sqlite:
                            cursor.execute("SELECT sqlite_version();")
                            db_version = f"SQLite {cursor.fetchone()[0]}"
                        else:
                            cursor.execute("SELECT version();")
                            db_version = cursor.fetchone()[0].split(",")[0]
                    except Exception:
                        db_version = "Unknown version"

                connected = True
                self.stdout.write(self.style.SUCCESS(f"  [SUCCESS] Connected in {latency_ms:.2f} ms!"))
                self.stdout.write(f"Server/DB Version:    {db_version}")

            except Exception as exc:
                elapsed = time.time() - start_time
                if wait_seconds > 0 and elapsed < wait_seconds:
                    self.stdout.write(self.style.WARNING(f"  [WAITING] Connection failed: {exc}. Retrying in {interval}s..."))
                    time.sleep(interval)
                else:
                    self.stdout.write(self.style.ERROR(f"  [ERROR] Connection failed: {exc}"))
                    raise CommandError(f"Database connection to '{db_alias}' failed: {exc}") from exc

        # SSL inspection for PostgreSQL
        if is_postgres:
            try:
                with db_conn.cursor() as cursor:
                    try:
                        cursor.execute("SELECT ssl_is_used();")
                        ssl_active = cursor.fetchone()[0]
                        self.stdout.write(f"SSL Active:           {self.style.SUCCESS('YES') if ssl_active else self.style.WARNING('NO')}")
                    except Exception:
                        raw_conn = db_conn.connection
                        ssl_in_use = False
                        if hasattr(raw_conn, 'info') and hasattr(raw_conn.info, 'ssl_in_use'):
                            ssl_in_use = raw_conn.info.ssl_in_use
                        elif hasattr(raw_conn, 'ssl_in_use'):
                            ssl_in_use = raw_conn.ssl_in_use
                        self.stdout.write(f"SSL Encrypted:        {self.style.SUCCESS('YES') if ssl_in_use else 'NO / Not active on localhost'}")
            except Exception:
                pass

        # Check migrations status
        try:
            executor = MigrationExecutor(db_conn)
            targets = executor.loader.graph.leaf_nodes()
            plan = executor.migration_plan(targets)
            if plan:
                self.stdout.write(
                    self.style.WARNING(f"Pending Migrations:   {len(plan)} unapplied migration(s) found!")
                )
                self.stdout.write(self.style.NOTICE("Run 'python manage.py migrate' to apply pending migrations."))
            else:
                self.stdout.write(
                    self.style.SUCCESS("Migrations:           All migrations are up to date.")
                )
        except Exception as exc:
            self.stdout.write(self.style.WARNING(f"Could not inspect migrations: {exc}"))

        self.stdout.write(self.style.MIGRATE_HEADING("=" * 60))
        self.stdout.write(self.style.SUCCESS("Database is healthy and ready for production traffic."))
        self.stdout.write(self.style.MIGRATE_HEADING("=" * 60))

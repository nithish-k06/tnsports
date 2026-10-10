from io import StringIO
from unittest.mock import patch
from django.test import TestCase
from django.core.management import call_command
from django.conf import settings
import dj_database_url


class ProductionDatabaseConfigTests(TestCase):
    def test_default_postgres_configuration(self):
        """Verify default database uses the PostgreSQL backend and required health checks."""
        db_conf = settings.DATABASES["default"]
        self.assertEqual(db_conf["ENGINE"], "django.db.backends.postgresql")
        self.assertTrue(db_conf.get("CONN_HEALTH_CHECKS"))
        self.assertIn("OPTIONS", db_conf)

    def test_database_url_parser_production(self):
        """Verify dj_database_url parses typical cloud production URLs (RDS, Supabase, Neon)."""
        test_url = "postgresql://produser:StrongPassword123@db.internal.cloud:5432/sports_prod?sslmode=require"
        parsed = dj_database_url.config(
            default=test_url,
            conn_max_age=600,
            conn_health_checks=True,
        )
        self.assertEqual(parsed["ENGINE"], "django.db.backends.postgresql")
        self.assertEqual(parsed["NAME"], "sports_prod")
        self.assertEqual(parsed["USER"], "produser")
        self.assertEqual(parsed["PASSWORD"], "StrongPassword123")
        self.assertEqual(parsed["HOST"], "db.internal.cloud")
        self.assertEqual(parsed["PORT"], 5432)
        self.assertEqual(parsed["CONN_MAX_AGE"], 600)
        self.assertTrue(parsed["CONN_HEALTH_CHECKS"])
        self.assertEqual(parsed.get("OPTIONS", {}).get("sslmode"), "require")

    def test_check_db_management_command_execution(self):
        """Verify check_db command runs against the active test database and reports success."""
        out = StringIO()
        call_command("check_db", stdout=out)
        output_str = out.getvalue()
        self.assertIn("POSTGRESQL PRODUCTION DATABASE CONNECTION CHECK", output_str)
        self.assertIn("[SUCCESS]", output_str)
        self.assertIn("Database is healthy", output_str)

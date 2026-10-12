import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Safely and idempotently create the initial superuser from environment variables without shell access."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            help="Superuser username (defaults to DJANGO_SUPERUSER_USERNAME or ADMIN_USERNAME env var)",
        )
        parser.add_argument(
            "--email",
            type=str,
            help="Superuser email (defaults to DJANGO_SUPERUSER_EMAIL or ADMIN_EMAIL env var)",
        )
        parser.add_argument(
            "--password",
            type=str,
            help="Superuser password (defaults to DJANGO_SUPERUSER_PASSWORD or ADMIN_PASSWORD env var)",
        )
        parser.add_argument(
            "--reset-password",
            action="store_true",
            help="Reset password if user already exists (also enabled by DJANGO_SUPERUSER_FORCE_PASSWORD_RESET=True)",
        )

    def handle(self, *args, **options):
        # 1. Read credentials from options or environment variables
        username = options.get("username") or os.getenv("DJANGO_SUPERUSER_USERNAME") or os.getenv("ADMIN_USERNAME")
        password = options.get("password") or os.getenv("DJANGO_SUPERUSER_PASSWORD") or os.getenv("ADMIN_PASSWORD")
        email = options.get("email") or os.getenv("DJANGO_SUPERUSER_EMAIL") or os.getenv("ADMIN_EMAIL") or "admin@example.com"
        reset_password = options.get("reset_password") or os.getenv("DJANGO_SUPERUSER_FORCE_PASSWORD_RESET", "").lower() in ("true", "1", "yes")

        # 2. Check if credentials were provided
        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    "[create_initial_superuser] No superuser credentials supplied in environment variables "
                    "(DJANGO_SUPERUSER_USERNAME / DJANGO_SUPERUSER_PASSWORD). Skipping initial admin creation."
                )
            )
            return

        username = username.strip()
        password = password.strip()
        email = email.strip()

        # 3. Check if user already exists
        user = User.objects.filter(username=username).first()

        if user:
            needs_save = False

            # Ensure staff and superuser flags
            if not user.is_superuser:
                user.is_superuser = True
                needs_save = True
            if not user.is_staff:
                user.is_staff = True
                needs_save = True
            if not user.is_active:
                user.is_active = True
                needs_save = True

            # Reset password if explicitly requested
            if reset_password:
                user.set_password(password)
                needs_save = True
                self.stdout.write(
                    self.style.SUCCESS(
                        f"[create_initial_superuser] Password for superuser '{username}' has been updated successfully."
                    )
                )

            if needs_save:
                user.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"[create_initial_superuser] Superuser '{username}' already exists. No duplicate created."
                )
            )
            return

        # 4. Create superuser
        try:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"[create_initial_superuser] Superuser '{username}' ({email}) created successfully!"
                )
            )
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(
                    f"[create_initial_superuser] Failed to create superuser: {e}"
                )
            )
            raise

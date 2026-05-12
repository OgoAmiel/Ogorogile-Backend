from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from leave_management.models import LeaveType, LeaveBalance


class Command(BaseCommand):
    help = "Create leave balance records for all employees for a specific leave type"

    def add_arguments(self, parser):
        parser.add_argument(
            "--leave-type-id",
            type=int,
            help="ID of the leave type to populate balances for",
        )
        parser.add_argument(
            "--leave-type-name",
            type=str,
            help="Name of the leave type to populate balances for",
        )

    def handle(self, *args, **options):
        User = get_user_model()

        leave_type_id = options.get("leave_type_id")
        leave_type_name = options.get("leave_type_name")

        if not leave_type_id and not leave_type_name:
            self.stdout.write(
                self.style.ERROR(
                    "Please provide either --leave-type-id or --leave-type-name"
                )
            )
            return

        try:
            if leave_type_id:
                leave_type = LeaveType.objects.get(id=leave_type_id)
            else:
                leave_type = LeaveType.objects.get(name=leave_type_name)
        except LeaveType.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    f"Leave type not found with the provided criteria"
                )
            )
            return

        users = User.objects.filter(is_active=True)

        balances_created = 0
        balances_already_exist = 0

        for user in users:
            _, created = LeaveBalance.objects.get_or_create(
                employee=user,
                leave_type=leave_type,
                defaults={
                    "total_days": leave_type.default_days,
                    "used_days": 0,
                },
            )

            if created:
                balances_created += 1
            else:
                balances_already_exist += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Leave balances created for '{leave_type.name}' successfully."
            )
        )
        self.stdout.write(self.style.SUCCESS(f"Users processed: {users.count()}"))
        self.stdout.write(
            self.style.SUCCESS(f"Leave balances created: {balances_created}")
        )
        self.stdout.write(
            self.style.WARNING(f"Leave balances already existing: {balances_already_exist}")
        )

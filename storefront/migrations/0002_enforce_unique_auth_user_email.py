from django.db import migrations
from django.db.models import Count
from django.db.models.functions import Lower


def validate_existing_user_emails(apps, schema_editor):
    User = apps.get_model("auth", "User")
    duplicates = list(
        User.objects.annotate(normalized_email=Lower("email"))
        .values("normalized_email")
        .annotate(total=Count("id"))
        .filter(total__gt=1)
        .order_by("normalized_email")
    )
    if not duplicates:
        return

    duplicate_labels = [
        entry["normalized_email"] or "<blank email>"
        for entry in duplicates[:5]
    ]
    raise RuntimeError(
        "Cannot add a unique constraint to auth_user.email until duplicate "
        f"addresses are cleaned up. Duplicates found: {', '.join(duplicate_labels)}"
    )


def add_unique_email_index(apps, schema_editor):
    schema_editor.execute(
        "CREATE UNIQUE INDEX auth_user_email_uniq ON auth_user (email);"
    )


def remove_unique_email_index(apps, schema_editor):
    if schema_editor.connection.vendor == "mysql":
        schema_editor.execute("DROP INDEX auth_user_email_uniq ON auth_user;")
        return

    schema_editor.execute("DROP INDEX auth_user_email_uniq;")


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("storefront", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            validate_existing_user_emails,
            migrations.RunPython.noop,
        ),
        migrations.RunPython(
            add_unique_email_index,
            remove_unique_email_index,
        ),
    ]

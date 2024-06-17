import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = "Syncs groups and permissions as defined in settings"

    def handle(self, *args, **options):
        for group_name, permissions in settings.GROUPS_PERMISSIONS.items():
            group, _ = Group.objects.get_or_create(name=group_name)
            group.permissions.clear()
            for code_name in permissions:
                print("Processing: %s" % code_name)
                p = Permission.objects.get(codename=code_name)
                group.permissions.add(p)

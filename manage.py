#!/usr/bin/env python3
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saleor.settings")
    os.environ.setdefault("DATABASE_URL", 'postgres://postgres:fhp7828493@localhost:5432/saleor')

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

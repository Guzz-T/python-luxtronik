"""Luxtronik helper scripts."""

def print_dump_header(caption):
    print("=" * 80)
    print(f"{' ' + caption + ' ': ^80}")
    print("=" * 80)

def print_dump_row(number, field):
    print(f"Number: {number:<5} Name: {field.name:<60} " + f"Type: {field.__class__.__name__:<20} Value: {field}")

def print_watch_header(caption):
    print("=" * 120)
    print(caption)
    print("=" * 120)
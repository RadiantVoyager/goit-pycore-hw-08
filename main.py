import pickle
from typing import Callable, Dict

from rich.console import Console
from rich.table import Table

from src.address_book import AddressBook, Record
from src.upcoming_birthdays import get_upcoming_birthdays


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return f"\n[red]{e.args[0]}"
        except KeyError as e:
            return f"\n[red]{e.args[0]}"
        except IndexError:
            return "\n[red]Enter user name."
        except Exception as e:
            return f"\n[red]{e}"

    return inner


def parse_input(user_input: str) -> tuple:
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


def say_to_hello(*_):
    return "\n[green] How can I help you?"


@input_error
def add_contact(args: list, book: AddressBook) -> str:
    name, phone, *_ = args
    record = book.find(name)
    message = "\n[green] Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "\n[green] Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_phone(args: list, book: AddressBook) -> str:
    name, old_phone, new_phone = args
    contact = book.find(name)
    if contact:
        contact.edit_phone(old_phone, new_phone)
        return "\n[green] Phone number changed."
    else:
        raise KeyError("There is no such a contact")


@input_error
def show_phone(args: list, book: AddressBook) -> str:
    name = args[0]
    contact = book.find(name)
    if contact:
        return f"\n[green]{', '.join([str(phone) for phone in contact.phones])}[/green]"
    else:
        raise KeyError("There is no such a contact.")


@input_error
def show_all(_, book: AddressBook) -> Table:
    table = Table(title="\nContacts", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Phone numbers", style="green")
    table.add_column("Birthday", style="blue")
    for contact in book.values():
        name = contact.name.value
        phone = ", ".join([str(phone) for phone in contact.phones])
        birthday = str(contact.birthday)
        table.add_row(name, phone, birthday)
    return table


@input_error
def add_birthday(args: list, book: AddressBook) -> str:
    name, birthday, *_ = args
    contact = book.find(name)
    if contact:
        contact.add_birthday(birthday)
        message = "\n[green] Contact updated."
        return message
    else:
        raise KeyError("There is no such a contact.")


@input_error
def show_birthday(args: list, book: AddressBook) -> str:
    name = args[0]
    contact = book.find(name)
    if contact:
        return f"\n[green]{contact.birthday}[/green]"
    else:
        raise KeyError("There is no such a contact.")


@input_error
def birthdays(_, book: AddressBook) -> str:
    all_entires = []
    for contact in book.values():
        name = contact.name.value
        birthday = str(contact.birthday)
        all_entires.append({"name": name, "birthday": birthday})
    upcoming_birthdays = get_upcoming_birthdays(all_entires)
    return f"\n[green]List of birthdays for the next 7 days: {upcoming_birthdays}"


def main():
    """
    The assistant bot
    """
    book = load_data()
    console = Console()
    # book = AddressBook()
    commands: Dict[str, Callable] = {
        "hello": say_to_hello,
        "add": add_contact,
        "change": change_phone,
        "phone": show_phone,
        "all": show_all,
        "add-birthday": add_birthday,
        "show-birthday": show_birthday,
        "birthdays": birthdays,
    }
    COMMANDS_DESCRIPTION = """
    Commands for the bot:
    hello -> get the question
    add <contact name> <phone number> -> add a new contact name and number
    change <contact name> <old phone number> <new phone number> -> change existing contact's phone number
    phone <contact name> -> get existing contact's phone number
    all -> get all existing contact's phone numbers
    add-birthday <contact name> <birthday> -> add birthday for existing contact name format DD.MM.YYYY
    show-birthday <contact name> -> get existing contact's birthday date
    birthdays -> get all existing contact's upcoming birthdays (during 7 days from now)
    close or exit -> close the bot
    """
    console.print(f"\n[yellow] Welcome to the assistant bot! \n{COMMANDS_DESCRIPTION}")
    while True:
        user_input = input("\n Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            console.print("\n[green] Good bye!\n")
            break
        elif command in commands:
            result = commands[command](args, book)
            console.print(result)
        else:
            console.print("\n[red] Invalid command.")
    save_data(book)


if __name__ == "__main__":
    main()

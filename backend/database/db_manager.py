from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, joinedload

from database.db_config import *


Session = sessionmaker(bind=engine)


def insert_test_data():
    Session = sessionmaker(bind=engine)
    session = Session()

    # Creating a single board
    board_main = Board(name='Main Board', emails=["grunet01@luther.edu", "kellca04@luther.edu"])

    # Tables for 'Main Board'
    table_todo = Table(name='To-Do', board=board_main, order=[])

    # Adding data to the session
    session.add_all([
        board_main, table_todo
    ])
    session.commit()


def view_data():
    Session = sessionmaker(bind=engine)
    session = Session()

    # Query and print data from the tables
    print("Boards:")
    for board in session.query(Board).all():
        print(f"Board ID: {board.id}, Name: {board.name}, Emails: {board.emails}")
        print("Tables:")
        for table in board.tables:
            print(f"  Table ID: {table.id}, Name: {table.name}")
            print("  Entries:")
            for entry in table.entries:
                print(f"    Entry ID: {entry.id}, Text: {entry.text}")
    print("\n")


def clear_database():
    Session = sessionmaker(bind=engine)
    session = Session()

    # Get all tables from metadata
    metadata = Base.metadata
    tables = metadata.sorted_tables

    # Delete all records from tables
    for table in reversed(tables):
        session.execute(table.delete())
    session.commit()


# Define functions for retrieving data
def get_boards_by_email(email):
    Session = sessionmaker(bind=engine)
    session = Session()

    boards = session.query(Board).filter(Board.emails.contains([email])).all()
    session.close()

    return boards


def get_tables(board_id):
    Session = sessionmaker(bind=engine)
    session = Session()

    tables = session.query(Table).options(joinedload(Table.entries)).filter_by(board_id=board_id).all()

    tables_with_entries = []
    for table in tables:
        table_data = {
            'id': table.id,
            'name': table.name,
            'entries': [{'id': entry.id, 'text': entry.text} for entry in table.entries],
            'order': table.order
        }
        tables_with_entries.append(table_data)

    session.close()
    return tables_with_entries


def get_entries(table_id):
    Session = sessionmaker(bind=engine)
    session = Session()

    entries = session.query(Entry).filter_by(table_id=table_id).all()
    session.close()
    
    return entries


# Define functions for modifying data
def upsert_board(name, board_id=None, user_email=None):
    session = Session()
    if board_id:
        board = session.query(Board).filter_by(id=board_id).first()
        if board:
            board.name = name
    else:
        new_board = Board(name=name, emails=[user_email])
        session.add(new_board)
    session.commit()
    session.close()


def upsert_table(board_id, name, table_id=None):
    session = Session()
    
    table = None
    if table_id:
        table = session.query(Table).filter_by(id=table_id).first()
        if table:
            table.name = name
    else:
        board = session.query(Board).filter_by(id=board_id).first()
    
        if not board:
            session.close()
            return None
        
        new_table = Table(name=name, board=board)
        session.add(new_table)
        table = new_table
    
    session.commit()

    if table:
        session.refresh(table)
    
    session.close()
    return table



def upsert_entry(table_id, text, entry_id=None):
    session = Session()
    
    entry = None
    if entry_id:
        entry = session.query(Entry).filter_by(id=entry_id).first()
        if entry:
            entry.text = text

    else:
        table = session.query(Table).filter_by(id=table_id).first()

        if not table:
            session.close()
            return None
        
        new_entry = Entry(text=text, table=table)
        session.add(new_entry)
        entry = new_entry

        session.commit()

        session.refresh(entry)
        table.order.append(entry.id)
        

    
    session.commit()
    session.close()

    return entry


def update_entry_table(entry_id, new_table_id):
    session = Session()
    entry = session.query(Entry).filter_by(id=entry_id).first()
    new_table = session.query(Table).filter_by(id=new_table_id).first()

    if entry and new_table:
        entry.table_id = new_table_id
        session.commit()
    
    session.close()


# Define functions for removing data
def remove_board(board_id):
    session = Session()
    board = session.query(Board).filter_by(id=board_id).first()

    if board:
        session.delete(board)
        session.commit()

    session.close()

def remove_table(table_id):
    session = Session()
    table = session.query(Table).filter_by(id=table_id).first()

    if table:
        session.delete(table)
        session.commit()

    session.close()

def remove_entry(entry_id):
    session = Session()
    entry = session.query(Entry).filter_by(id=entry_id).first()

    if entry:
        session.delete(entry)
        session.commit()

    session.close()
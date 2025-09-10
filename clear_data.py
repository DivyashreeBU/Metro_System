from app import app, db
from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker

with app.app_context():
    metadata = MetaData()
    metadata.reflect(bind=db.engine)

    Session = sessionmaker(bind=db.engine)
    session = Session()

    try:
        for table in reversed(metadata.sorted_tables):
            if table.name != 'admin':
                session.execute(table.delete())
        session.commit()
        print("✅ All data deleted except 'admin' table.")
    except Exception as e:
        session.rollback()
        print("❌ Error:", e)
    finally:
        session.close()
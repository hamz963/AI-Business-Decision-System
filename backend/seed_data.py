import os
from app.core.database import SessionLocal, Base, engine
from app.core.security import get_password_hash
from app.models.organization import Organization
from app.models.user import User
from app.models.dataset import Dataset
from app.models.kpi import KPIDefinition
from app.models.decision import Decision
from app.services.data_ingestion import data_ingestion_service
from app.services.kpi_calculator import kpi_calculator

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # 1. Organization
    org = db.query(Organization).filter(Organization.slug == "acme-global").first()
    if not org:
        org = Organization(name="Acme Global Enterprise", slug="acme-global")
        db.add(org)
        db.commit()
        db.refresh(org)
        print("Created Organization: Acme Global Enterprise")

    # 2. Administrator User
    admin = db.query(User).filter(User.email == "admin@acme.com").first()
    if not admin:
        admin = User(
            org_id=org.id,
            email="admin@acme.com",
            hashed_password=get_password_hash("Admin1234!"),
            full_name="Alex Drake",
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print("Created User: admin@acme.com / Admin1234!")

    # 3. Ingest Demo Dataset
    csv_path = os.path.abspath("demo_data/enterprise_sales_sample.csv")
    if os.path.exists(csv_path):
        existing_ds = db.query(Dataset).filter(Dataset.org_id == org.id, Dataset.name == "Enterprise Historical Sales (24M)").first()
        if not existing_ds:
            table_name, row_count, col_count, quality_score, schema_info, quality_report = (
                data_ingestion_service.ingest_file(
                    file_path=csv_path,
                    org_id=org.id,
                    original_filename="enterprise_sales_sample.csv"
                )
            )

            ds = Dataset(
                org_id=org.id,
                name="Enterprise Historical Sales (24M)",
                description="Complete 24-month multi-region sales ledger with seasonal variations and cost structure.",
                source_type="csv",
                file_path=csv_path,
                table_name=table_name,
                row_count=row_count,
                column_count=col_count,
                schema_info=schema_info,
                quality_score=quality_score,
                quality_report=quality_report
            )
            db.add(ds)
            db.commit()
            print(f"Ingested Demo Dataset: {ds.name} ({row_count} rows, Quality Score: {quality_score}/100)")

    db.close()
    print("Database seeding completed successfully.")

if __name__ == "__main__":
    seed()

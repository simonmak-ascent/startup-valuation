import { getDb } from "./client";
import { TABLES } from "./schema";

export async function migrate(): Promise<void> {
  const db = await getDb();

  await db.query(`
    DEFINE TABLE ${TABLES.VALUATION_RUN} SCHEMAFULL;
    DEFINE FIELD method ON ${TABLES.VALUATION_RUN} TYPE record<${TABLES.METHOD}>;
    DEFINE FIELD user ON ${TABLES.VALUATION_RUN} TYPE option<record<${TABLES.USER}>>;
    DEFINE FIELD inputs ON ${TABLES.VALUATION_RUN} TYPE string;
    DEFINE FIELD result ON ${TABLES.VALUATION_RUN} TYPE float;
    DEFINE FIELD steps ON ${TABLES.VALUATION_RUN} TYPE string;
    DEFINE FIELD formula_number ON ${TABLES.VALUATION_RUN} TYPE string;
    DEFINE FIELD chapter ON ${TABLES.VALUATION_RUN} TYPE string;
    DEFINE FIELD library_version ON ${TABLES.VALUATION_RUN} TYPE string;
    DEFINE FIELD git_commit ON ${TABLES.VALUATION_RUN} TYPE option<string>;
    DEFINE FIELD audit_log ON ${TABLES.VALUATION_RUN} TYPE option<record<${TABLES.AUDIT_LOG}>>;
    DEFINE FIELD created_at ON ${TABLES.VALUATION_RUN} TYPE datetime DEFAULT time::now();
    DEFINE FIELD ip_hash ON ${TABLES.VALUATION_RUN} TYPE option<string>;
    DEFINE INDEX idx_valuation_method ON ${TABLES.VALUATION_RUN} COLUMNS method, created_at;
    DEFINE INDEX idx_valuation_user ON ${TABLES.VALUATION_RUN} COLUMNS user;
  `);

  await db.query(`
    DEFINE TABLE ${TABLES.METHOD} SCHEMAFULL;
    DEFINE FIELD name ON ${TABLES.METHOD} TYPE string;
    DEFINE FIELD slug ON ${TABLES.METHOD} TYPE string;
    DEFINE FIELD module ON ${TABLES.METHOD} TYPE string;
    DEFINE FIELD function_name ON ${TABLES.METHOD} TYPE string;
    DEFINE FIELD category ON ${TABLES.METHOD} TYPE string;
    DEFINE FIELD description ON ${TABLES.METHOD} TYPE string;
    DEFINE FIELD inputs_schema ON ${TABLES.METHOD} TYPE object;
    DEFINE FIELD textbook_chapter ON ${TABLES.METHOD} TYPE option<string>;
    DEFINE FIELD formula_numbers ON ${TABLES.METHOD} TYPE array;
    DEFINE FIELD citations ON ${TABLES.METHOD} TYPE array<record<${TABLES.CITATION}>>;
    DEFINE FIELD assumptions ON ${TABLES.METHOD} TYPE array<record<${TABLES.ASSUMPTION}>>;
    DEFINE FIELD created_at ON ${TABLES.METHOD} TYPE datetime DEFAULT time::now();
    DEFINE FIELD updated_at ON ${TABLES.METHOD} TYPE option<datetime>;
  `);

  await db.query(`
    DEFINE TABLE ${TABLES.ASSUMPTION} SCHEMAFULL;
    DEFINE FIELD name ON ${TABLES.ASSUMPTION} TYPE string;
    DEFINE FIELD value ON ${TABLES.ASSUMPTION} TYPE float;
    DEFINE FIELD unit ON ${TABLES.ASSUMPTION} TYPE option<string>;
    DEFINE FIELD valid_from ON ${TABLES.ASSUMPTION} TYPE datetime;
    DEFINE FIELD valid_until ON ${TABLES.ASSUMPTION} TYPE option<datetime>;
    DEFINE FIELD source_url ON ${TABLES.ASSUMPTION} TYPE string;
    DEFINE FIELD source_name ON ${TABLES.ASSUMPTION} TYPE string;
    DEFINE FIELD source_retrieved_at ON ${TABLES.ASSUMPTION} TYPE datetime;
    DEFINE FIELD source_version ON ${TABLES.ASSUMPTION} TYPE string;
    DEFINE FIELD created_at ON ${TABLES.ASSUMPTION} TYPE datetime DEFAULT time::now();
    DEFINE INDEX idx_assumption_current ON ${TABLES.ASSUMPTION} COLUMNS name, valid_until;
  `);

  await db.query(`
    DEFINE TABLE ${TABLES.USER} SCHEMAFULL;
    DEFINE FIELD clerk_id ON ${TABLES.USER} TYPE string;
    DEFINE FIELD email ON ${TABLES.USER} TYPE string;
    DEFINE FIELD name ON ${TABLES.USER} TYPE option<string>;
    DEFINE FIELD avatar_url ON ${TABLES.USER} TYPE option<string>;
    DEFINE FIELD tier ON ${TABLES.USER} TYPE string DEFAULT "free";
    DEFINE FIELD preferences ON ${TABLES.USER} TYPE object DEFAULT {};
    DEFINE FIELD saved_calculations ON ${TABLES.USER} TYPE array<record<${TABLES.VALUATION_RUN}>>;
    DEFINE FIELD created_at ON ${TABLES.USER} TYPE datetime DEFAULT time::now();
    DEFINE FIELD last_active_at ON ${TABLES.USER} TYPE option<datetime>;
  `);

  await db.query(`
    DEFINE TABLE ${TABLES.AUDIT_LOG} SCHEMAFULL;
    DEFINE FIELD valuation_run ON ${TABLES.AUDIT_LOG} TYPE record<${TABLES.VALUATION_RUN}>;
    DEFINE FIELD user ON ${TABLES.AUDIT_LOG} TYPE option<record<${TABLES.USER}>>;
    DEFINE FIELD action ON ${TABLES.AUDIT_LOG} TYPE string;
    DEFINE FIELD method ON ${TABLES.AUDIT_LOG} TYPE string;
    DEFINE FIELD inputs ON ${TABLES.AUDIT_LOG} TYPE string;
    DEFINE FIELD result ON ${TABLES.AUDIT_LOG} TYPE float;
    DEFINE FIELD steps ON ${TABLES.AUDIT_LOG} TYPE string;
    DEFINE FIELD formula_number ON ${TABLES.AUDIT_LOG} TYPE string;
    DEFINE FIELD chapter ON ${TABLES.AUDIT_LOG} TYPE string;
    DEFINE FIELD library_version ON ${TABLES.AUDIT_LOG} TYPE string;
    DEFINE FIELD git_commit ON ${TABLES.AUDIT_LOG} TYPE option<string>;
    DEFINE FIELD client_ip_hash ON ${TABLES.AUDIT_LOG} TYPE option<string>;
    DEFINE FIELD user_agent ON ${TABLES.AUDIT_LOG} TYPE option<string>;
    DEFINE FIELD created_at ON ${TABLES.AUDIT_LOG} TYPE datetime DEFAULT time::now();
    DEFINE INDEX idx_audit_created ON ${TABLES.AUDIT_LOG} COLUMNS created_at;
    DEFINE INDEX idx_audit_user ON ${TABLES.AUDIT_LOG} COLUMNS user;
  `);

  await db.query(`
    DEFINE EVENT audit_log_immutable ON TABLE ${TABLES.AUDIT_LOG}
      WHEN $event = "UPDATE" OR $event = "DELETE" THEN
        THROW "audit_log is immutable: UPDATE and DELETE are forbidden";
  `);

  await db.query(`
    DEFINE TABLE ${TABLES.DATA_SOURCE} SCHEMAFULL;
    DEFINE FIELD name ON ${TABLES.DATA_SOURCE} TYPE string;
    DEFINE FIELD url ON ${TABLES.DATA_SOURCE} TYPE string;
    DEFINE FIELD reputation ON ${TABLES.DATA_SOURCE} TYPE string DEFAULT "Unknown";
    DEFINE FIELD description ON ${TABLES.DATA_SOURCE} TYPE string;
    DEFINE FIELD access_method ON ${TABLES.DATA_SOURCE} TYPE string;
    DEFINE FIELD refresh_frequency ON ${TABLES.DATA_SOURCE} TYPE string;
    DEFINE FIELD last_validated_at ON ${TABLES.DATA_SOURCE} TYPE option<datetime>;
    DEFINE FIELD created_at ON ${TABLES.DATA_SOURCE} TYPE datetime DEFAULT time::now();
  `);

  await db.query(`
    DEFINE TABLE ${TABLES.PUBLIC_COMPANY} SCHEMAFULL;
    DEFINE FIELD name ON ${TABLES.PUBLIC_COMPANY} TYPE string;
    DEFINE FIELD ticker ON ${TABLES.PUBLIC_COMPANY} TYPE option<string>;
    DEFINE FIELD industry ON ${TABLES.PUBLIC_COMPANY} TYPE record<${TABLES.INDUSTRY}>;
    DEFINE FIELD sector ON ${TABLES.PUBLIC_COMPANY} TYPE option<string>;
    DEFINE FIELD country ON ${TABLES.PUBLIC_COMPANY} TYPE option<string>;
    DEFINE FIELD description ON ${TABLES.PUBLIC_COMPANY} TYPE option<string>;
    DEFINE FIELD employees ON ${TABLES.PUBLIC_COMPANY} TYPE option<int>;
    DEFINE FIELD founded_year ON ${TABLES.PUBLIC_COMPANY} TYPE option<int>;
    DEFINE FIELD source_url ON ${TABLES.PUBLIC_COMPANY} TYPE string;
    DEFINE FIELD source_name ON ${TABLES.PUBLIC_COMPANY} TYPE string;
    DEFINE FIELD source_retrieved_at ON ${TABLES.PUBLIC_COMPANY} TYPE datetime;
    DEFINE FIELD source_version ON ${TABLES.PUBLIC_COMPANY} TYPE string;
    DEFINE FIELD created_at ON ${TABLES.PUBLIC_COMPANY} TYPE datetime DEFAULT time::now();
    DEFINE INDEX idx_pubco_industry ON ${TABLES.PUBLIC_COMPANY} COLUMNS industry, country;
  `);

  await db.query(`
    DEFINE TABLE ${TABLES.VALUATION_EVENT} SCHEMAFULL;
    DEFINE FIELD company ON ${TABLES.VALUATION_EVENT} TYPE record<${TABLES.PUBLIC_COMPANY}>;
    DEFINE FIELD valuation_amount ON ${TABLES.VALUATION_EVENT} TYPE float;
    DEFINE FIELD valuation_date ON ${TABLES.VALUATION_EVENT} TYPE datetime;
    DEFINE FIELD event_type ON ${TABLES.VALUATION_EVENT} TYPE string;
    DEFINE FIELD stage ON ${TABLES.VALUATION_EVENT} TYPE option<string>;
    DEFINE FIELD method_used ON ${TABLES.VALUATION_EVENT} TYPE option<record<${TABLES.METHOD}>>;
    DEFINE FIELD currency ON ${TABLES.VALUATION_EVENT} TYPE string DEFAULT "USD";
    DEFINE FIELD source_url ON ${TABLES.VALUATION_EVENT} TYPE string;
    DEFINE FIELD source_name ON ${TABLES.VALUATION_EVENT} TYPE string;
    DEFINE FIELD source_retrieved_at ON ${TABLES.VALUATION_EVENT} TYPE datetime;
    DEFINE FIELD source_version ON ${TABLES.VALUATION_EVENT} TYPE string;
    DEFINE FIELD created_at ON ${TABLES.VALUATION_EVENT} TYPE datetime DEFAULT time::now();
    DEFINE INDEX idx_val_event_company ON ${TABLES.VALUATION_EVENT} COLUMNS company, valuation_date;
    DEFINE INDEX idx_val_event_stage ON ${TABLES.VALUATION_EVENT} COLUMNS stage, event_type;
  `);

  await db.query(`
    DEFINE TABLE ${TABLES.FINANCIAL_METRIC} SCHEMAFULL;
    DEFINE FIELD company ON ${TABLES.FINANCIAL_METRIC} TYPE record<${TABLES.PUBLIC_COMPANY}>;
    DEFINE FIELD metric_name ON ${TABLES.FINANCIAL_METRIC} TYPE string;
    DEFINE FIELD metric_value ON ${TABLES.FINANCIAL_METRIC} TYPE float;
    DEFINE FIELD unit ON ${TABLES.FINANCIAL_METRIC} TYPE string;
    DEFINE FIELD period ON ${TABLES.FINANCIAL_METRIC} TYPE string;
    DEFINE FIELD filing_date ON ${TABLES.FINANCIAL_METRIC} TYPE option<datetime>;
    DEFINE FIELD source_url ON ${TABLES.FINANCIAL_METRIC} TYPE string;
    DEFINE FIELD source_name ON ${TABLES.FINANCIAL_METRIC} TYPE string;
    DEFINE FIELD source_retrieved_at ON ${TABLES.FINANCIAL_METRIC} TYPE datetime;
    DEFINE FIELD source_version ON ${TABLES.FINANCIAL_METRIC} TYPE string;
    DEFINE FIELD created_at ON ${TABLES.FINANCIAL_METRIC} TYPE datetime DEFAULT time::now();
    DEFINE INDEX idx_finmetric_company ON ${TABLES.FINANCIAL_METRIC} COLUMNS company, metric_name, period;
  `);

  await db.query(`
    DEFINE TABLE ${TABLES.INDUSTRY} SCHEMAFULL;
    DEFINE FIELD name ON ${TABLES.INDUSTRY} TYPE string;
    DEFINE FIELD parent ON ${TABLES.INDUSTRY} TYPE option<record<${TABLES.INDUSTRY}>>;
    DEFINE FIELD description ON ${TABLES.INDUSTRY} TYPE option<string>;
    DEFINE FIELD created_at ON ${TABLES.INDUSTRY} TYPE datetime DEFAULT time::now();
  `);

  await db.query(`
    DEFINE TABLE ${TABLES.BENCHMARK} SCHEMAFULL;
    DEFINE FIELD version ON ${TABLES.BENCHMARK} TYPE string;
    DEFINE FIELD industry ON ${TABLES.BENCHMARK} TYPE record<${TABLES.INDUSTRY}>;
    DEFINE FIELD stage ON ${TABLES.BENCHMARK} TYPE option<string>;
    DEFINE FIELD metric ON ${TABLES.BENCHMARK} TYPE string;
    DEFINE FIELD value ON ${TABLES.BENCHMARK} TYPE float;
    DEFINE FIELD p25 ON ${TABLES.BENCHMARK} TYPE option<float>;
    DEFINE FIELD p75 ON ${TABLES.BENCHMARK} TYPE option<float>;
    DEFINE FIELD count ON ${TABLES.BENCHMARK} TYPE int;
    DEFINE FIELD source_records ON ${TABLES.BENCHMARK} TYPE array<record<${TABLES.VALUATION_EVENT}>>;
    DEFINE FIELD computed_at ON ${TABLES.BENCHMARK} TYPE datetime;
    DEFINE FIELD created_at ON ${TABLES.BENCHMARK} TYPE datetime DEFAULT time::now();
    DEFINE INDEX idx_benchmark_lookup ON ${TABLES.BENCHMARK} COLUMNS version, industry, stage;
  `);

  await db.query(`
    DEFINE TABLE ${TABLES.CITATION} SCHEMAFULL;
    DEFINE FIELD title ON ${TABLES.CITATION} TYPE string;
    DEFINE FIELD authors ON ${TABLES.CITATION} TYPE array;
    DEFINE FIELD year ON ${TABLES.CITATION} TYPE int;
    DEFINE FIELD type ON ${TABLES.CITATION} TYPE string;
    DEFINE FIELD doi ON ${TABLES.CITATION} TYPE option<string>;
    DEFINE FIELD url ON ${TABLES.CITATION} TYPE option<string>;
    DEFINE FIELD bibtex ON ${TABLES.CITATION} TYPE option<string>;
    DEFINE FIELD source_url ON ${TABLES.CITATION} TYPE string;
    DEFINE FIELD source_name ON ${TABLES.CITATION} TYPE string;
    DEFINE FIELD source_retrieved_at ON ${TABLES.CITATION} TYPE datetime;
    DEFINE FIELD source_version ON ${TABLES.CITATION} TYPE string;
    DEFINE FIELD created_at ON ${TABLES.CITATION} TYPE datetime DEFAULT time::now();
  `);

  await db.query(`
    DEFINE TABLE ${TABLES.ETL_RUN} SCHEMAFULL;
    DEFINE FIELD job_name ON ${TABLES.ETL_RUN} TYPE string;
    DEFINE FIELD status ON ${TABLES.ETL_RUN} TYPE string;
    DEFINE FIELD records_imported ON ${TABLES.ETL_RUN} TYPE int DEFAULT 0;
    DEFINE FIELD records_rejected ON ${TABLES.ETL_RUN} TYPE int DEFAULT 0;
    DEFINE FIELD errors ON ${TABLES.ETL_RUN} TYPE array;
    DEFINE FIELD started_at ON ${TABLES.ETL_RUN} TYPE datetime;
    DEFINE FIELD completed_at ON ${TABLES.ETL_RUN} TYPE option<datetime>;
    DEFINE FIELD created_at ON ${TABLES.ETL_RUN} TYPE datetime DEFAULT time::now();
    DEFINE INDEX idx_etl_job ON ${TABLES.ETL_RUN} COLUMNS job_name, started_at;
  `);

  await db.query(`
    DEFINE TABLE ${TABLES.SUBSCRIPTION} SCHEMAFULL;
    DEFINE FIELD user_id ON ${TABLES.SUBSCRIPTION} TYPE string;
    DEFINE FIELD stripe_subscription_id ON ${TABLES.SUBSCRIPTION} TYPE string;
    DEFINE FIELD stripe_customer_id ON ${TABLES.SUBSCRIPTION} TYPE string;
    DEFINE FIELD tier ON ${TABLES.SUBSCRIPTION} TYPE string DEFAULT 'free';
    DEFINE FIELD status ON ${TABLES.SUBSCRIPTION} TYPE string;
    DEFINE FIELD current_period_end ON ${TABLES.SUBSCRIPTION} TYPE option<datetime>;
    DEFINE FIELD created_at ON ${TABLES.SUBSCRIPTION} TYPE datetime DEFAULT time::now();
    DEFINE FIELD updated_at ON ${TABLES.SUBSCRIPTION} TYPE option<datetime>;
    DEFINE INDEX idx_subscription_stripe ON ${TABLES.SUBSCRIPTION} COLUMNS stripe_subscription_id UNIQUE;
    DEFINE INDEX idx_subscription_user ON ${TABLES.SUBSCRIPTION} COLUMNS user_id;
  `);

  await db.query(`
    DEFINE TABLE ${TABLES.PAYMENT_EVENT} SCHEMAFULL;
    DEFINE FIELD stripe_event_id ON ${TABLES.PAYMENT_EVENT} TYPE string;
    DEFINE FIELD type ON ${TABLES.PAYMENT_EVENT} TYPE string;
    DEFINE FIELD payload ON ${TABLES.PAYMENT_EVENT} TYPE string;
    DEFINE FIELD processed_at ON ${TABLES.PAYMENT_EVENT} TYPE datetime DEFAULT time::now();
    DEFINE INDEX idx_payment_event_stripe ON ${TABLES.PAYMENT_EVENT} COLUMNS stripe_event_id UNIQUE;
  `);

  await db.query(`
    DEFINE EVENT payment_event_immutable ON TABLE ${TABLES.PAYMENT_EVENT}
      WHEN $event = "UPDATE" OR $event = "DELETE" THEN
        THROW "payment_event is append-only";
  `);

  await db.query(`
    DEFINE TABLE ${TABLES.LEGAL_DOCUMENT} SCHEMAFULL;
    DEFINE FIELD slug ON ${TABLES.LEGAL_DOCUMENT} TYPE string;
    DEFINE FIELD version ON ${TABLES.LEGAL_DOCUMENT} TYPE string;
    DEFINE FIELD title ON ${TABLES.LEGAL_DOCUMENT} TYPE string;
    DEFINE FIELD body ON ${TABLES.LEGAL_DOCUMENT} TYPE string;
    DEFINE FIELD content_hash ON ${TABLES.LEGAL_DOCUMENT} TYPE string;
    DEFINE FIELD published_at ON ${TABLES.LEGAL_DOCUMENT} TYPE datetime DEFAULT time::now();
    DEFINE INDEX idx_legal_slug ON ${TABLES.LEGAL_DOCUMENT} COLUMNS slug, version UNIQUE;
  `);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  migrate()
    .then(() => {
      process.exit(0);
    })
    .catch((error) => {
      console.error("Migration failed:", error);
      process.exit(1);
    });
}

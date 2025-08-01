CREATE TABLE
    "AWS_COST_REPORT" (
        "ACCOUNT_UUID" VARCHAR(40) NOT NULL,
        "COMPANY" VARCHAR(1000),
        "COST_CATEGORY" VARCHAR(100) NOT NULL,
        "COST" DECIMAL(24, 2) NOT NULL,
        "STATUS" VARCHAR(50) NOT NULL,
        "START_DATE" DATE NOT NULL,
        CONSTRAINT "PK" PRIMARY KEY ("ACCOUNT_UUID", "COST_CATEGORY", "START_DATE")
    );

CREATE VIEW
    CUSTOMERS AS
SELECT DISTINCT
    account_uuid,
    company,
    status
FROM
    consumption_report cr
WHERE
    report_generated_at = (
        SELECT
            MAX(report_generated_at)
        FROM
            consumption_report
        WHERE
            account_uuid = cr.account_uuid
    );
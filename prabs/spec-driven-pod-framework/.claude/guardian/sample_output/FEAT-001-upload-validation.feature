Feature: Document Upload and Validation
  As a system user
  I want to upload PDF documents for processing
  So that the AI extraction pipeline can analyse their content

  Background:
    Given the upload service is running
    And the virus scanner is available

  @REQ-001 @upload-service @happy-path
  Scenario: Accept valid PDF at size boundary
    Given a PDF file of exactly 50MB
    When the file is uploaded via POST /api/documents/upload
    Then the response status is 200
    And the response body contains a document_id
    And the document_id is a valid UUID

  @REQ-001 @upload-service @boundary @negative
  Scenario: Reject PDF exceeding size limit
    Given a PDF file of 50.1MB
    When the file is uploaded via POST /api/documents/upload
    Then the response status is 413
    And the response body contains error code "DOC_TOO_LARGE"

  @REQ-001 @upload-service @negative
  Scenario: Reject non-PDF file format
    Given a DOCX file of 5MB
    When the file is uploaded via POST /api/documents/upload
    Then the response status is 415
    And the response body contains error code "UNSUPPORTED_FORMAT"

  @REQ-002 @security-service @happy-path
  Scenario: Clean document proceeds to processing within SLA
    Given a clean PDF document has been uploaded
    When the virus scanner completes its scan
    Then processing begins within 5 seconds
    And the document status transitions from SCANNING to PROCESSING

  @REQ-002 @security-service @negative
  Scenario: Infected document is quarantined
    Given a document flagged by the virus scanner
    When the scan result is received
    Then the document status transitions to QUARANTINED
    And no extraction processing is initiated
    And the document_id is added to the quarantine registry

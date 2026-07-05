BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "analytics_aggregatedresult" (
	"id"	integer NOT NULL,
	"level"	varchar(20) NOT NULL,
	"entity_name"	varchar(255) NOT NULL,
	"entity_code"	varchar(50),
	"total_responses"	integer unsigned NOT NULL CHECK("total_responses" >= 0),
	"average_score"	real NOT NULL,
	"raw_data"	text NOT NULL CHECK((JSON_VALID("raw_data") OR "raw_data" IS NULL)),
	"calculated_at"	datetime NOT NULL,
	"year"	integer unsigned NOT NULL CHECK("year" >= 0),
	"quarter"	integer unsigned CHECK("quarter" >= 0),
	"survey_id"	bigint NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("survey_id") REFERENCES "survey_survey"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "analytics_comparisonreport" (
	"id"	integer NOT NULL,
	"name"	varchar(255) NOT NULL,
	"comparison_type"	varchar(50) NOT NULL,
	"report_data"	text NOT NULL CHECK((JSON_VALID("report_data") OR "report_data" IS NULL)),
	"generated_at"	datetime NOT NULL,
	"export_file"	varchar(100),
	"survey_id"	bigint NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("survey_id") REFERENCES "survey_survey"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "analytics_scoringconfig" (
	"id"	integer NOT NULL,
	"name"	varchar(255) NOT NULL,
	"criteria_mapping"	text NOT NULL CHECK((JSON_VALID("criteria_mapping") OR "criteria_mapping" IS NULL)),
	"created_at"	datetime NOT NULL,
	"is_active"	bool NOT NULL,
	"survey_id"	bigint NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("survey_id") REFERENCES "survey_survey"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "analytics_targetgroup" (
	"id"	integer NOT NULL,
	"code"	varchar(50) NOT NULL UNIQUE,
	"name"	varchar(255) NOT NULL,
	"description"	text,
	"icon"	varchar(50) NOT NULL,
	"is_active"	bool NOT NULL,
	"forms"	text NOT NULL CHECK((JSON_VALID("forms") OR "forms" IS NULL)),
	"created_at"	datetime NOT NULL,
	"updated_at"	datetime NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "analytics_targetgroup_surveys" (
	"id"	integer NOT NULL,
	"targetgroup_id"	bigint NOT NULL,
	"survey_id"	bigint NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("survey_id") REFERENCES "survey_survey"("id") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("targetgroup_id") REFERENCES "analytics_targetgroup"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "survey_blocklist" (
	"id"	integer NOT NULL,
	"block_type"	varchar(20) NOT NULL,
	"value"	varchar(255) NOT NULL,
	"reason"	text,
	"created_at"	datetime NOT NULL,
	"expires_at"	datetime,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "survey_question" (
	"id"	integer NOT NULL,
	"title"	varchar(500) NOT NULL,
	"description"	text,
	"is_required"	bool NOT NULL,
	"order"	integer unsigned NOT NULL CHECK("order" >= 0),
	"options"	text NOT NULL CHECK((JSON_VALID("options") OR "options" IS NULL)),
	"condition_logic"	text NOT NULL CHECK((JSON_VALID("condition_logic") OR "condition_logic" IS NULL)),
	"config"	text NOT NULL CHECK((JSON_VALID("config") OR "config" IS NULL)),
	"created_at"	datetime NOT NULL,
	"updated_at"	datetime NOT NULL,
	"question_type_id"	bigint NOT NULL,
	"section_id"	bigint NOT NULL,
	"component_type"	varchar(50) NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("question_type_id") REFERENCES "survey_questiontype"("id") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("section_id") REFERENCES "survey_section"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "survey_questiontype" (
	"id"	integer NOT NULL,
	"name"	varchar(100) NOT NULL UNIQUE,
	"code"	varchar(50) NOT NULL UNIQUE,
	"icon"	varchar(50),
	"has_options"	bool NOT NULL,
	"has_validation"	bool NOT NULL,
	"created_at"	datetime NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "survey_response" (
	"id"	integer NOT NULL,
	"respondent_ip"	char(39),
	"respondent_device_id"	varchar(255),
	"respondent_email"	varchar(254),
	"user_agent"	text,
	"started_at"	datetime NOT NULL,
	"time_taken"	integer unsigned NOT NULL CHECK("time_taken" >= 0),
	"answers"	text NOT NULL CHECK((JSON_VALID("answers") OR "answers" IS NULL)),
	"is_verified"	bool NOT NULL,
	"verification_token"	varchar(64),
	"is_cleaned"	bool NOT NULL,
	"is_duplicate"	bool NOT NULL,
	"created_at"	datetime NOT NULL,
	"user_id"	bigint,
	"survey_id"	bigint NOT NULL,
	"section_progress"	text NOT NULL CHECK((JSON_VALID("section_progress") OR "section_progress" IS NULL)),
	"status"	varchar(20) NOT NULL,
	"submitted_at"	datetime,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("survey_id") REFERENCES "survey_survey"("id") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("user_id") REFERENCES "accounts_user"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "survey_section" (
	"id"	integer NOT NULL,
	"code"	varchar(10) NOT NULL,
	"title"	varchar(255) NOT NULL,
	"description"	text,
	"icon"	varchar(50),
	"order"	integer unsigned NOT NULL CHECK("order" >= 0),
	"created_at"	datetime NOT NULL,
	"updated_at"	datetime NOT NULL,
	"survey_id"	bigint NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("survey_id") REFERENCES "survey_survey"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "survey_survey" (
	"id"	integer NOT NULL,
	"title"	varchar(255) NOT NULL,
	"slug"	varchar(255) NOT NULL UNIQUE,
	"description"	text,
	"start_date"	datetime NOT NULL,
	"end_date"	datetime NOT NULL,
	"allow_after_deadline"	bool NOT NULL,
	"status"	varchar(20) NOT NULL,
	"target_groups"	text NOT NULL CHECK((JSON_VALID("target_groups") OR "target_groups" IS NULL)),
	"settings"	text NOT NULL CHECK((JSON_VALID("settings") OR "settings" IS NULL)),
	"created_at"	datetime NOT NULL,
	"updated_at"	datetime NOT NULL,
	"category_id"	bigint,
	"code"	varchar(20) UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("category_id") REFERENCES "survey_surveycategory"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "survey_surveyassignment" (
	"id"	integer NOT NULL,
	"form_code"	varchar(20) NOT NULL,
	"form_name"	varchar(255) NOT NULL,
	"form_description"	text,
	"target_group_code"	varchar(50) NOT NULL,
	"target_group_name"	varchar(255) NOT NULL,
	"target_group_description"	text,
	"is_active"	bool NOT NULL,
	"order"	integer unsigned NOT NULL CHECK("order" >= 0),
	"created_at"	datetime NOT NULL,
	"updated_at"	datetime NOT NULL,
	"section_id"	bigint,
	"survey_id"	bigint NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("section_id") REFERENCES "survey_section"("id") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("survey_id") REFERENCES "survey_survey"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "survey_surveycategory" (
	"id"	integer NOT NULL,
	"name"	varchar(255) NOT NULL UNIQUE,
	"description"	text,
	"icon"	varchar(50),
	"created_at"	datetime NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "survey_surveyparticipant" (
	"id"	integer NOT NULL,
	"agency"	varchar(255) NOT NULL,
	"target_group_code"	varchar(50) NOT NULL,
	"target_group_name"	varchar(255) NOT NULL,
	"full_name"	varchar(255) NOT NULL,
	"position"	varchar(255) NOT NULL,
	"department"	varchar(255) NOT NULL,
	"phone"	varchar(20) NOT NULL,
	"email"	varchar(254) NOT NULL,
	"notes"	text,
	"assigned_forms"	text NOT NULL CHECK((JSON_VALID("assigned_forms") OR "assigned_forms" IS NULL)),
	"ip_address"	char(39),
	"user_agent"	text,
	"session_key"	varchar(64),
	"status"	varchar(20) NOT NULL,
	"submitted_at"	datetime,
	"created_at"	datetime NOT NULL,
	"updated_at"	datetime NOT NULL,
	"response_id"	bigint UNIQUE,
	"survey_id"	bigint NOT NULL,
	"user_id"	bigint,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("response_id") REFERENCES "survey_response"("id") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("survey_id") REFERENCES "survey_survey"("id") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("user_id") REFERENCES "accounts_user"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "survey_surveyprogress" (
	"id"	integer NOT NULL,
	"form_code"	varchar(20) NOT NULL,
	"status"	varchar(20) NOT NULL,
	"progress_percent"	integer unsigned NOT NULL CHECK("progress_percent" >= 0),
	"started_at"	datetime,
	"completed_at"	datetime,
	"last_accessed_at"	datetime NOT NULL,
	"created_at"	datetime NOT NULL,
	"participant_id"	bigint NOT NULL,
	"response_id"	bigint UNIQUE,
	"survey_id"	bigint,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("participant_id") REFERENCES "survey_surveyparticipant"("id") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("response_id") REFERENCES "survey_response"("id") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("survey_id") REFERENCES "survey_survey"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "survey_surveyunitstatus" (
	"id"	integer NOT NULL,
	"status"	varchar(20) NOT NULL,
	"completed_count"	integer unsigned NOT NULL CHECK("completed_count" >= 0),
	"total_assignees"	integer unsigned NOT NULL CHECK("total_assignees" >= 0),
	"completed_at"	datetime,
	"updated_at"	datetime NOT NULL,
	"organization_id"	bigint NOT NULL,
	"survey_id"	bigint NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("organization_id") REFERENCES "accounts_organization"("id") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("survey_id") REFERENCES "survey_survey"("id") DEFERRABLE INITIALLY DEFERRED
);
INSERT INTO "analytics_targetgroup" ("id","code","name","description","icon","is_active","forms","created_at","updated_at") VALUES (1,'GRP001','Nhóm đối tượng 1','','bi-people',1,'["BM-09", "BM-08", "BM-03"]','2026-06-30 08:00:07.901295','2026-07-01 06:16:55.388668'),
 (2,'GRP002','Nhóm đối tượng 2','','bi-people',1,'["BM-09", "BM-08", "BM-06", "BM-04"]','2026-06-30 09:22:23.522484','2026-07-01 06:16:52.675632'),
 (3,'GRP003','Nhóm đối tượng 3','','bi-people',1,'["BM-09", "BM-07", "BM-06", "BM-05"]','2026-07-01 06:09:46.666948','2026-07-01 06:16:50.442880');
INSERT INTO "survey_question" ("id","title","description","is_required","order","options","condition_logic","config","created_at","updated_at","question_type_id","section_id","component_type") VALUES (6784,'BM-04: Phiếu khảo sát cán bộ chuyên trách CCHC','',0,0,'[]','{}','{}','2026-07-01 02:57:59.294238','2026-07-01 02:57:59.294252',8,319,'question'),
 (6785,'Thu thập thông tin từ cán bộ trực tiếp thực hiện công tác CCHC nhằm:','',0,0,'[]','{}','{}','2026-07-01 02:57:59.306857','2026-07-01 02:57:59.306870',9,319,'question'),
 (6786,'• Khảo sát chi tiết quy trình nghiệp vụ hiện nay.
• Đánh giá hiện trạng quản lý kế hoạch, nhiệm vụ CCHC.
• Đánh giá hiện trạng quản lý hồ sơ minh chứng.
• Đánh giá quy trình tự đánh giá, chấm điểm, thẩm định.
• Xác định khó khăn, vướng mắc trong quá trình thực hiện.
• Thu thập yêu cầu nghiệp vụ đối với Hệ thống theo dõi, đánh giá CCHC.','',0,0,'[]','{}','{}','2026-07-01 02:57:59.319838','2026-07-01 02:57:59.319850',9,319,'question'),
 (6787,'Họ và tên:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 02:57:59.434531','2026-07-01 02:57:59.434544',1,320,'question'),
 (6788,'Chức vụ:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 02:57:59.446273','2026-07-01 02:57:59.446286',1,320,'question'),
 (6789,'Đơn vị công tác:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 02:57:59.458555','2026-07-01 02:57:59.458567',1,320,'question'),
 (6790,'Bộ phận:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 02:57:59.470657','2026-07-01 02:57:59.470669',1,320,'question'),
 (6791,'Số năm tham gia công tác CCHC:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 02:57:59.483124','2026-07-01 02:57:59.483136',1,320,'question'),
 (6792,'Điện thoại:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 02:57:59.495117','2026-07-01 02:57:59.495130',1,320,'question'),
 (6793,'Email:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 02:57:59.507253','2026-07-01 02:57:59.507266',1,320,'question'),
 (6794,'A. THÔNG TIN HIỆN TRẠNG','',0,0,'[]','{}','{}','2026-07-01 02:57:59.909589','2026-07-01 02:57:59.909602',8,321,'question'),
 (6795,'1. Công tác lập kế hoạch CCHC','',0,0,'[]','{}','{}','2026-07-01 02:57:59.967497','2026-07-01 02:57:59.967537',8,321,'question'),
 (6796,'a. Đơn vị lập kế hoạch CCHC theo chu kỳ nào?','',0,0,'["N\u0103m", "Qu\u00fd", "Th\u00e1ng"]','{}','{"options": ["N\u0103m", "Qu\u00fd", "Th\u00e1ng"]}','2026-07-01 02:57:59.982776','2026-07-01 02:57:59.982789',4,321,'question'),
 (6797,'b. Trung bình mỗi năm có bao nhiêu nhiệm vụ CCHC?','Số lượng: .....',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 02:57:59.997825','2026-07-01 02:57:59.997842',1,321,'question'),
 (6798,'c. Công cụ hiện đang sử dụng để quản lý kế hoạch?','',0,0,'["Word", "Excel", "Ph\u1ea7n m\u1ec1m"]','{}','{"options": ["Word", "Excel", "Ph\u1ea7n m\u1ec1m"]}','2026-07-01 02:58:00.012508','2026-07-01 02:58:00.012523',4,321,'question'),
 (6799,'d. Quy trình giao nhiệm vụ hiện nay như thế nào?','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 02:58:00.027330','2026-07-01 02:58:00.027346',2,321,'question'),
 (6800,'e. Việc cập nhật tiến độ được thực hiện như thế nào?','',0,0,'["Theo ng\u00e0y", "Theo tu\u1ea7n", "Theo th\u00e1ng", "Theo qu\u00fd", "Theo giai \u0111o\u1ea1n", "Theo y\u00eau c\u1ea7u"]','{}','{"options": ["Theo ng\u00e0y", "Theo tu\u1ea7n", "Theo th\u00e1ng", "Theo qu\u00fd", "Theo giai \u0111o\u1ea1n", "Theo y\u00eau c\u1ea7u"]}','2026-07-01 02:58:00.039964','2026-07-01 02:58:00.039976',4,321,'question'),
 (6801,'g. Những khó khăn trong quản lý kế hoạch hiện nay?','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 02:58:00.053359','2026-07-01 02:58:00.053375',2,321,'question'),
 (6802,'2. Quản lý nhiệm vụ CCHC','',0,0,'[]','{}','{}','2026-07-01 02:58:00.067293','2026-07-01 02:58:00.067306',8,321,'question'),
 (6803,'a. Hiện nay nhiệm vụ được giao theo đơn vị hay cá nhân?','',0,0,'["Theo \u0111\u01a1n v\u1ecb", "Theo c\u00e1 nh\u00e2n"]','{}','{"options": ["Theo \u0111\u01a1n v\u1ecb", "Theo c\u00e1 nh\u00e2n"]}','2026-07-01 02:58:00.082439','2026-07-01 02:58:00.082456',3,321,'question'),
 (6804,'b. Các trạng thái nhiệm vụ cần theo dõi?','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 02:58:00.098107','2026-07-01 02:58:00.098121',2,321,'question'),
 (6805,'c. Đơn vị có sử dụng cơ chế cảnh báo quá hạn không?','',0,0,'["C\u00f3", "Kh\u00f4ng"]','{}','{"options": ["C\u00f3", "Kh\u00f4ng"]}','2026-07-01 02:58:00.112464','2026-07-01 02:58:00.112478',3,321,'question'),
 (6806,'d. Việc tổng hợp tiến độ hiện nay thực hiện như thế nào?','',0,0,'["Theo ng\u00e0y", "Theo tu\u1ea7n", "Theo th\u00e1ng", "Theo qu\u00fd", "Theo giai \u0111o\u1ea1n", "Theo y\u00eau c\u1ea7u"]','{}','{"options": ["Theo ng\u00e0y", "Theo tu\u1ea7n", "Theo th\u00e1ng", "Theo qu\u00fd", "Theo giai \u0111o\u1ea1n", "Theo y\u00eau c\u1ea7u"]}','2026-07-01 02:58:00.125912','2026-07-01 02:58:00.125926',4,321,'question'),
 (6807,'e. Trung bình mỗi tháng có bao nhiêu nhiệm vụ cần theo dõi?','Số lượng: .....',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 02:58:00.140565','2026-07-01 02:58:00.140580',1,321,'question'),
 (6808,'g. Các khó khăn khi theo dõi nhiệm vụ?','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 02:58:00.154636','2026-07-01 02:58:00.154649',2,321,'question'),
 (6809,'3. Đánh giá mức độ khó khăn','',0,0,'[]','{}','{"grid_type": "yesno", "criteria_label": "N\u1ed9i dung", "scale": [{"value": 1, "label": "Kh\u00f4ng"}, {"value": 2, "label": "\u00cdt"}, {"value": 3, "label": "Trung b\u00ecnh"}, {"value": 4, "label": "Nhi\u1ec1u"}, {"value": 5, "label": "R\u1ea5t nhi\u1ec1u"}], "criteria": ["Theo d\u00f5i ti\u1ebfn \u0111\u1ed9", "\u0110\u00f4n \u0111\u1ed1c th\u1ef1c hi\u1ec7n", "T\u1ed5ng h\u1ee3p k\u1ebft qu\u1ea3", "Qu\u1ea3n l\u00fd th\u1eddi h\u1ea1n"]}','2026-07-01 02:58:00.168456','2026-07-01 02:58:00.168471',5,321,'question'),
 (6810,'4. Quản lý hồ sơ minh chứng','',0,0,'[]','{}','{}','2026-07-01 02:58:00.181781','2026-07-01 02:58:00.181795',8,321,'question'),
 (6811,'a. Hiện trạng hồ sơ minh chứng','',0,0,'[]','{}','{"grid_type": "yesno", "criteria_label": "C\u00e2u h\u1ecfi kh\u1ea3o s\u00e1t", "scale": [{"value": 1, "label": "Tr\u1ea3 l\u1eddi"}, {"value": 2, "label": "C\u00f3"}, {"value": 3, "label": "Kh\u00f4ng"}], "criteria": ["C\u00e1c lo\u1ea1i h\u1ed3 s\u01a1 minh ch\u1ee9ng \u0111ang qu\u1ea3n l\u00fd?", "H\u1ed3 s\u01a1 \u0111\u01b0\u1ee3c l\u01b0u \u1edf \u0111\u00e2u?", "H\u00ecnh th\u1ee9c l\u01b0u tr\u1eef?", "Trung b\u00ecnh m\u1ed7i n\u0103m ph\u00e1t sinh bao nhi\u00eau h\u1ed3 s\u01a1?", "Dung l\u01b0\u1ee3ng d\u1eef li\u1ec7u minh ch\u1ee9ng \u01b0\u1edbc t\u00ednh?", "Quy tr\u00ecnh ki\u1ec3m tra v\u00e0 ph\u00ea duy\u1ec7t h\u1ed3 s\u01a1?"]}','2026-07-01 02:58:00.195803','2026-07-01 02:58:00.195817',5,321,'question'),
 (6812,'b. Đánh giá khó khăn','',0,0,'[]','{}','{"grid_type": "yesno", "criteria_label": "N\u1ed9i dung", "scale": [{"value": 1, "label": "Kh\u00f4ng"}, {"value": 2, "label": "\u00cdt"}, {"value": 3, "label": "TB"}, {"value": 4, "label": "Nhi\u1ec1u"}, {"value": 5, "label": "R\u1ea5t nhi\u1ec1u"}], "criteria": ["Thu th\u1eadp minh ch\u1ee9ng", "Ki\u1ec3m tra minh ch\u1ee9ng", "T\u00ecm ki\u1ebfm h\u1ed3 s\u01a1", "T\u1ed5ng h\u1ee3p minh ch\u1ee9ng"]}','2026-07-01 02:58:00.209124','2026-07-01 02:58:00.209139',5,321,'question'),
 (6813,'5. Công tác tự đánh giá và chấm điểm CCHC','',0,0,'[]','{}','{}','2026-07-01 02:58:00.222832','2026-07-01 02:58:00.222846',8,321,'question'),
 (6814,'a. Quy trình chấm điểm','',0,0,'[]','{}','{"columns": ["STT", "C\u00e2u h\u1ecfi", "Tr\u1ea3 l\u1eddi"], "data": [["1", "Hi\u1ec7n nay vi\u1ec7c ch\u1ea5m \u0111i\u1ec3m th\u1ef1c hi\u1ec7n b\u1eb1ng c\u00f4ng c\u1ee5 g\u00ec?", ""], ["2", "Ai l\u00e0 ng\u01b0\u1eddi nh\u1eadp \u0111i\u1ec3m?", ""], ["3", "Ai l\u00e0 ng\u01b0\u1eddi th\u1ea9m \u0111\u1ecbnh?", ""], ["4", "Ai l\u00e0 ng\u01b0\u1eddi ph\u00ea duy\u1ec7t?", ""], ["5", "Vi\u1ec7c t\u00ednh \u0111i\u1ec3m hi\u1ec7n nay c\u00f3 t\u1ef1 \u0111\u1ed9ng kh\u00f4ng?", ""], ["6", "C\u00f3 l\u01b0u l\u1ecbch s\u1eed thay \u0111\u1ed5i \u0111i\u1ec3m kh\u00f4ng?", ""]], "rows": 6}','2026-07-01 02:58:00.236986','2026-07-01 02:58:00.237000',6,321,'question'),
 (6815,'b. Đánh giá khó khăn','',0,0,'[]','{}','{"grid_type": "yesno", "criteria_label": "N\u1ed9i dung", "scale": [{"value": 1, "label": "Kh\u00f4ng"}, {"value": 2, "label": "\u00cdt"}, {"value": 3, "label": "TB"}, {"value": 4, "label": "Nhi\u1ec1u"}, {"value": 5, "label": "R\u1ea5t nhi\u1ec1u"}], "criteria": ["Nh\u1eadp d\u1eef li\u1ec7u \u0111\u00e1nh gi\u00e1", "T\u00ednh \u0111i\u1ec3m", "\u0110\u1ed1i chi\u1ebfu minh ch\u1ee9ng", "T\u1ed5ng h\u1ee3p k\u1ebft qu\u1ea3"]}','2026-07-01 02:58:00.250426','2026-07-01 02:58:00.250440',5,321,'question'),
 (6816,'6. Công tác báo cáo','',0,0,'[]','{}','{}','2026-07-01 02:58:00.264822','2026-07-01 02:58:00.264835',8,321,'question'),
 (6817,'a. Các loại báo cáo','',0,0,'[]','{}','{"columns": ["STT", "B\u00e1o c\u00e1o", "T\u1ea7n su\u1ea5t"], "data": [["1", "B\u00e1o c\u00e1o th\u00e1ng", ""], ["2", "B\u00e1o c\u00e1o qu\u00fd", ""], ["3", "B\u00e1o c\u00e1o 6 th\u00e1ng", ""], ["4", "B\u00e1o c\u00e1o n\u0103m", ""], ["5", "B\u00e1o c\u00e1o chuy\u00ean \u0111\u1ec1", ""]], "rows": 5}','2026-07-01 02:58:00.277596','2026-07-01 02:58:00.277608',6,321,'question'),
 (6818,'b. Khó khăn khi lập báo cáo','',0,0,'[]','{}','{"grid_type": "yesno", "criteria_label": "N\u1ed9i dung", "scale": [{"value": 1, "label": "Kh\u00f4ng"}, {"value": 2, "label": "\u00cdt"}, {"value": 3, "label": "TB"}, {"value": 4, "label": "Nhi\u1ec1u"}, {"value": 5, "label": "R\u1ea5t nhi\u1ec1u"}], "criteria": ["Thu th\u1eadp d\u1eef li\u1ec7u", "T\u1ed5ng h\u1ee3p s\u1ed1 li\u1ec7u", "Ki\u1ec3m tra s\u1ed1 li\u1ec7u", "Xu\u1ea5t b\u00e1o c\u00e1o"]}','2026-07-01 02:58:00.290052','2026-07-01 02:58:00.290064',5,321,'question'),
 (6819,'7. Phần mềm đang sử dụng','',0,0,'[]','{}','{}','2026-07-01 02:58:00.301884','2026-07-01 02:58:00.301896',8,321,'question'),
 (6820,'a. Hiện trạng phần mềm','',0,0,'[]','{}','{"columns": ["STT", "T\u00ean ph\u1ea7n m\u1ec1m", "Ch\u1ee9c n\u0103ng", "\u0110\u00e1nh gi\u00e1"], "data": [["1", "", "", ""], ["2", "", "", ""]], "rows": 2}','2026-07-01 02:58:00.316327','2026-07-01 02:58:00.316344',6,321,'question'),
 (6821,'b. Mức độ đáp ứng','',0,0,'[]','{}','{"grid_type": "yesno", "criteria_label": "Ti\u00eau ch\u00ed", "scale": [{"value": 1, "label": "R\u1ea5t t\u1ed1t"}, {"value": 2, "label": "T\u1ed1t"}, {"value": 3, "label": "TB"}, {"value": 4, "label": "K\u00e9m"}], "criteria": ["Qu\u1ea3n l\u00fd k\u1ebf ho\u1ea1ch", "Qu\u1ea3n l\u00fd nhi\u1ec7m v\u1ee5", "Qu\u1ea3n l\u00fd minh ch\u1ee9ng", "Ch\u1ea5m \u0111i\u1ec3m", "B\u00e1o c\u00e1o"]}','2026-07-01 02:58:00.329298','2026-07-01 02:58:00.329310',5,321,'question'),
 (6822,'c. Những hạn chế lớn nhất','',0,0,'["Thi\u1ebfu ch\u1ee9c n\u0103ng", "Kh\u00f3 s\u1eed d\u1ee5ng", "Ch\u1eadm", "Kh\u00f4ng c\u00f3 Dashboard", "Thi\u1ebfu t\u00edch h\u1ee3p", "Kh\u00f3 t\u1ed5ng h\u1ee3p d\u1eef li\u1ec7u", "Kh\u00e1c: _____________"]','{}','{"options": ["Thi\u1ebfu ch\u1ee9c n\u0103ng", "Kh\u00f3 s\u1eed d\u1ee5ng", "Ch\u1eadm", "Kh\u00f4ng c\u00f3 Dashboard", "Thi\u1ebfu t\u00edch h\u1ee3p", "Kh\u00f3 t\u1ed5ng h\u1ee3p d\u1eef li\u1ec7u", "Kh\u00e1c: _____________"]}','2026-07-01 02:58:00.348507','2026-07-01 02:58:00.348519',4,321,'question'),
 (6823,'B. YÊU CẦU ĐỐI VỚI HỆ THỐNG MỚI','',0,0,'[]','{}','{}','2026-07-01 02:58:00.360970','2026-07-01 02:58:00.360981',8,321,'question'),
 (6824,'1. Chức năng mong muốn','(1 = Không cần; 5 = Rất cần)',0,0,'[]','{}','{"grid_type": "scale5", "criteria_label": "Ch\u1ee9c n\u0103ng", "scale": [{"value": 1, "label": "1"}, {"value": 2, "label": "2"}, {"value": 3, "label": "3"}, {"value": 4, "label": "4"}, {"value": 5, "label": "5"}], "criteria": ["Qu\u1ea3n l\u00fd k\u1ebf ho\u1ea1ch", "Qu\u1ea3n l\u00fd nhi\u1ec7m v\u1ee5", "Qu\u1ea3n l\u00fd minh ch\u1ee9ng \u0111i\u1ec7n t\u1eed", "T\u1ef1 \u0111\u1ed9ng t\u00ednh \u0111i\u1ec3m", "T\u1ef1 \u0111\u1ed9ng t\u1ed5ng h\u1ee3p b\u00e1o c\u00e1o", "Dashboard tr\u1ef1c quan", "C\u1ea3nh b\u00e1o qu\u00e1 h\u1ea1n", "App Mobile", "K\u00fd s\u1ed1 h\u1ed3 s\u01a1", "T\u00edch h\u1ee3p h\u1ec7 th\u1ed1ng kh\u00e1c"]}','2026-07-01 02:58:00.372470','2026-07-01 02:58:00.372482',5,321,'question'),
 (6825,'2. Tiện ích AI mong muốn','',0,0,'[]','{}','{"grid_type": "yesno", "criteria_label": "Ti\u1ec7n \u00edch", "scale": [{"value": 1, "label": "C\u00f3 nhu c\u1ea7u"}, {"value": 2, "label": "Kh\u00f4ng"}], "criteria": ["AI h\u1ed7 tr\u1ee3 t\u1ed5ng h\u1ee3p b\u00e1o c\u00e1o", "AI h\u1ed7 tr\u1ee3 ki\u1ec3m tra minh ch\u1ee9ng", "AI h\u1ed7 tr\u1ee3 ph\u00e2n t\u00edch d\u1eef li\u1ec7u CCHC", "AI Chatbot h\u1ed7 tr\u1ee3 s\u1eed d\u1ee5ng h\u1ec7 th\u1ed1ng", "AI t\u00ecm ki\u1ebfm th\u00f4ng minh h\u1ed3 s\u01a1"]}','2026-07-01 02:58:00.385144','2026-07-01 02:58:00.385155',5,321,'question'),
 (6826,'1. Ba khó khăn lớn nhất hiện nay','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 02:58:00.440988','2026-07-01 02:58:00.441002',2,322,'question'),
 (6827,'2. Ba chức năng quan trọng nhất hệ thống cần có','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 02:58:00.455801','2026-07-01 02:58:00.455814',2,322,'question'),
 (7340,'BM-05: Phiếu khảo sát hiện trạng ứng dụng CNTT','',0,0,'[]','{}','{}','2026-07-01 05:15:21.133996','2026-07-01 05:15:21.134009',8,335,'question'),
 (7341,'Thu thập thông tin về hiện trạng ứng dụng CNTT tại các cơ quan, đơn vị phục vụ công tác cải cách hành chính nhằm:','',0,0,'[]','{}','{}','2026-07-01 05:15:21.147603','2026-07-01 05:15:21.147619',9,335,'question'),
 (7342,'• Đánh giá mức độ ứng dụng CNTT trong công tác CCHC.
• Khảo sát các hệ thống phần mềm đang sử dụng.
• Đánh giá khả năng đáp ứng nghiệp vụ của các hệ thống hiện tại.
• Xác định khả năng kế thừa dữ liệu, tích hợp hệ thống.
• Đánh giá hiện trạng hạ tầng kỹ thuật, người dùng và vận hành.
• Thu thập nhu cầu nâng cấp, thay thế hoặc bổ sung chức năng.','',0,0,'[]','{}','{}','2026-07-01 05:15:21.161402','2026-07-01 05:15:21.161415',9,335,'question'),
 (7343,'Đơn vị:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 05:15:21.275750','2026-07-01 05:15:21.275763',1,336,'question'),
 (7344,'Người cung cấp:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 05:15:21.289333','2026-07-01 05:15:21.289350',1,336,'question'),
 (7345,'Chức vụ:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 05:15:21.301961','2026-07-01 05:15:21.301974',1,336,'question'),
 (7346,'Bộ phận:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 05:15:21.314935','2026-07-01 05:15:21.314948',1,336,'question'),
 (7347,'Điện thoại:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 05:15:21.328753','2026-07-01 05:15:21.328765',1,336,'question'),
 (7348,'Email:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 05:15:21.342015','2026-07-01 05:15:21.342030',1,336,'question'),
 (7349,'A. HIỆN TRẠNG ỨNG DỤNG CNTT','',0,0,'[]','{}','{}','2026-07-01 05:15:21.620605','2026-07-01 05:15:21.620618',8,337,'question'),
 (7350,'1. Mức độ ứng dụng CNTT trong công tác CCHC','',0,0,'[]','{}','{}','2026-07-01 05:15:21.635204','2026-07-01 05:15:21.635220',8,337,'question'),
 (7351,'a. Đơn vị hiện đang sử dụng CNTT ở mức độ nào trong công tác CCHC?','',0,0,'[]','{}','{"grid_type": "checklist", "criteria_label": "M\u1ee9c \u0111\u1ed9", "scale": [{"value": 1, "label": "Ch\u1ecdn", "kind": "checkbox"}], "criteria": ["Ho\u00e0n to\u00e0n th\u1ee7 c\u00f4ng", "K\u1ebft h\u1ee3p gi\u1ea5y t\u1edd v\u00e0 Excel", "C\u00f3 ph\u1ea7n m\u1ec1m h\u1ed7 tr\u1ee3 m\u1ed9t ph\u1ea7n", "\u0110\u00e3 s\u1ed1 h\u00f3a ph\u1ea7n l\u1edbn quy tr\u00ecnh", "Ho\u00e0n to\u00e0n tr\u00ean m\u00f4i tr\u01b0\u1eddng s\u1ed1"]}','2026-07-01 05:15:21.650604','2026-07-01 05:15:21.650616',5,337,'question'),
 (7352,'b. Các hoạt động nào hiện nay đã được tin học hóa?','',0,0,'[]','{}','{"grid_type": "yesno", "criteria_label": "N\u1ed9i dung", "scale": [{"value": 1, "label": "C\u00f3", "kind": "radio"}, {"value": 2, "label": "Kh\u00f4ng", "kind": "radio"}], "criteria": ["L\u1eadp k\u1ebf ho\u1ea1ch CCHC", "Qu\u1ea3n l\u00fd nhi\u1ec7m v\u1ee5", "Qu\u1ea3n l\u00fd h\u1ed3 s\u01a1 minh ch\u1ee9ng", "Ch\u1ea5m \u0111i\u1ec3m CCHC", "B\u00e1o c\u00e1o th\u1ed1ng k\u00ea", "Dashboard \u0111i\u1ec1u h\u00e0nh"]}','2026-07-01 05:15:21.664981','2026-07-01 05:15:21.664994',5,337,'question'),
 (7353,'2. Khảo sát phần mềm đang sử dụng','',0,0,'[]','{}','{}','2026-07-01 05:15:21.679038','2026-07-01 05:15:21.679050',8,337,'question'),
 (7354,'a. Danh mục phần mềm hiện có','',0,0,'[]','{}','{"columns": ["STT", "T\u00ean ph\u1ea7n m\u1ec1m", "\u0110\u01a1n v\u1ecb cung c\u1ea5p", "N\u0103m tri\u1ec3n khai", "M\u1ee5c \u0111\u00edch s\u1eed d\u1ee5ng"], "data": [["1", "", "", "", ""], ["2", "", "", "", ""], ["3", "", "", "", ""]], "rows": 3}','2026-07-01 05:15:21.693369','2026-07-01 05:15:21.693387',6,337,'question'),
 (7355,'b. Hình thức sử dụng','',0,0,'[]','{}','{"grid_type": "checklist", "criteria_label": "H\u00ecnh th\u1ee9c", "scale": [{"value": 1, "label": "C\u00f3", "kind": "checkbox"}], "criteria": ["Thu\u00ea d\u1ecbch v\u1ee5 SaaS", "Thu\u00ea h\u1ea1 t\u1ea7ng Cloud", "D\u00f9ng chung c\u1ee7a Th\u00e0nh ph\u1ed1", "T\u1ef1 \u0111\u1ea7u t\u01b0, v\u1eadn h\u00e0nh", "Thu\u00ea ngo\u00e0i qu\u1ea3n tr\u1ecb v\u1eadn h\u00e0nh"]}','2026-07-01 05:15:21.708146','2026-07-01 05:15:21.708159',5,337,'question'),
 (7356,'c. Thông tin chi tiết phần mềm','Áp dụng cho từng phần mềm, chức năng đang sử dụng:',0,0,'[]','{}','{"grid_type": "checklist", "criteria_label": "Ch\u1ee9c n\u0103ng", "scale": [{"value": 1, "label": "C\u00f3 s\u1eed d\u1ee5ng", "kind": "checkbox"}], "criteria": ["Qu\u1ea3n l\u00fd k\u1ebf ho\u1ea1ch", "Qu\u1ea3n l\u00fd nhi\u1ec7m v\u1ee5", "Qu\u1ea3n l\u00fd h\u1ed3 s\u01a1 minh ch\u1ee9ng", "Qu\u1ea3n l\u00fd quy tr\u00ecnh x\u1eed l\u00fd", "Ch\u1ea5m \u0111i\u1ec3m CCHC", "B\u00e1o c\u00e1o th\u1ed1ng k\u00ea", "Dashboard \u0111i\u1ec1u h\u00e0nh", "Qu\u1ea3n tr\u1ecb ng\u01b0\u1eddi d\u00f9ng"]}','2026-07-01 05:15:21.724454','2026-07-01 05:15:21.724469',5,337,'question'),
 (7357,'d. Đánh giá mức độ đáp ứng','',0,0,'[]','{}','{"grid_type": "scale5", "criteria_label": "Ti\u00eau ch\u00ed", "scale": [{"value": 1, "label": "1", "kind": "radio"}, {"value": 2, "label": "2", "kind": "radio"}, {"value": 3, "label": "3", "kind": "radio"}, {"value": 4, "label": "4", "kind": "radio"}, {"value": 5, "label": "5", "kind": "radio"}], "criteria": ["Giao di\u1ec7n s\u1eed d\u1ee5ng", "T\u1ed1c \u0111\u1ed9 x\u1eed l\u00fd", "\u0110\u1ed9 \u1ed5n \u0111\u1ecbnh", "Kh\u1ea3 n\u0103ng b\u00e1o c\u00e1o", "Dashboard", "Kh\u1ea3 n\u0103ng t\u00ecm ki\u1ebfm d\u1eef li\u1ec7u", "Kh\u1ea3 n\u0103ng t\u00edch h\u1ee3p"]}','2026-07-01 05:15:21.738745','2026-07-01 05:15:21.738758',5,337,'question'),
 (7358,'3. Khảo sát dữ liệu và khả năng kế thừa','',0,0,'[]','{}','{}','2026-07-01 05:15:21.752481','2026-07-01 05:15:21.752493',8,337,'question'),
 (7359,'a. Hiện trạng dữ liệu','Các nhóm dữ liệu hiện có',0,0,'[]','{}','{"grid_type": "checklist", "criteria_label": "Nh\u00f3m d\u1eef li\u1ec7u", "scale": [{"value": 1, "label": "C\u00f3 d\u1eef li\u1ec7u", "kind": "checkbox"}, {"value": 2, "label": "Kh\u1ed1i l\u01b0\u1ee3ng", "kind": "text"}], "criteria": ["K\u1ebf ho\u1ea1ch CCHC", "Nhi\u1ec7m v\u1ee5 CCHC", "H\u1ed3 s\u01a1 minh ch\u1ee9ng", "K\u1ebft qu\u1ea3 \u0111\u00e1nh gi\u00e1", "B\u00e1o c\u00e1o t\u1ed5ng h\u1ee3p", "Ng\u01b0\u1eddi d\u00f9ng"]}','2026-07-01 05:15:21.765329','2026-07-01 05:15:21.765342',5,337,'question'),
 (7360,'b. Định dạng dữ liệu','',0,0,'[]','{}','{"grid_type": "checklist", "criteria_label": "Lo\u1ea1i d\u1eef li\u1ec7u", "scale": [{"value": 1, "label": "C\u00f3", "kind": "checkbox"}], "criteria": ["Excel", "Word", "PDF", "SQL Server", "Oracle", "PostgreSQL", "MySQL", "Kh\u00e1c"]}','2026-07-01 05:15:21.779690','2026-07-01 05:15:21.779709',5,337,'question'),
 (7361,'c. Khả năng kế thừa dữ liệu','',0,0,'[]','{}','{"grid_type": "yesno", "criteria_label": "N\u1ed9i dung", "scale": [{"value": 1, "label": "C\u00f3 th\u1ec3 k\u1ebf th\u1eeba", "kind": "radio"}, {"value": 2, "label": "Kh\u00f4ng", "kind": "radio"}], "criteria": ["Danh m\u1ee5c \u0111\u01a1n v\u1ecb", "Danh m\u1ee5c ng\u01b0\u1eddi d\u00f9ng", "D\u1eef li\u1ec7u k\u1ebf ho\u1ea1ch CCHC", "D\u1eef li\u1ec7u \u0111\u00e1nh gi\u00e1", "H\u1ed3 s\u01a1 minh ch\u1ee9ng"]}','2026-07-01 05:15:21.792751','2026-07-01 05:15:21.792764',5,337,'question'),
 (7362,'d. Nhu cầu chia sẻ dữ liệu','',0,0,'[]','{}','{"grid_type": "yesno", "criteria_label": "N\u1ed9i dung", "scale": [{"value": 1, "label": "C\u00f3", "kind": "radio"}, {"value": 2, "label": "Kh\u00f4ng", "kind": "radio"}], "criteria": ["Chia s\u1ebb d\u1eef li\u1ec7u v\u1edbi S\u1edf N\u1ed9i v\u1ee5", "Chia s\u1ebb d\u1eef li\u1ec7u v\u1edbi c\u00e1c S\u1edf ng\u00e0nh", "Chia s\u1ebb d\u1eef li\u1ec7u v\u1edbi x\u00e3/ph\u01b0\u1eddng", "K\u1ebft n\u1ed1i kho d\u1eef li\u1ec7u d\u00f9ng chung"]}','2026-07-01 05:15:21.807601','2026-07-01 05:15:21.807615',5,337,'question'),
 (7363,'4. Đánh giá hạn chế của hệ thống hiện tại','',0,0,'[]','{}','{}','2026-07-01 05:15:21.821143','2026-07-01 05:15:21.821157',8,337,'question'),
 (7364,'a. Các tồn tại, khó khăn','',0,0,'[]','{}','{"grid_type": "checklist", "criteria_label": "N\u1ed9i dung", "scale": [{"value": 1, "label": "C\u00f3 g\u1eb7p", "kind": "checkbox"}], "criteria": ["H\u1ec7 th\u1ed1ng ho\u1ea1t \u0111\u1ed9ng ch\u1eadm", "Kh\u00f3 s\u1eed d\u1ee5ng", "Thi\u1ebfu b\u00e1o c\u00e1o", "Thi\u1ebfu Dashboard", "Kh\u00f3 t\u00ecm ki\u1ebfm d\u1eef li\u1ec7u", "Kh\u00f4ng h\u1ed7 tr\u1ee3 thi\u1ebft b\u1ecb di \u0111\u1ed9ng", "Thi\u1ebfu c\u1ea3nh b\u00e1o t\u1ef1 \u0111\u1ed9ng", "Thi\u1ebfu t\u00edch h\u1ee3p d\u1eef li\u1ec7u", "Kh\u00f3 qu\u1ea3n l\u00fd h\u1ed3 s\u01a1 minh ch\u1ee9ng", "Kh\u00e1c"]}','2026-07-01 05:15:21.836067','2026-07-01 05:15:21.836080',5,337,'question'),
 (7365,'b. Mức độ ảnh hưởng','',0,0,'[]','{}','{"grid_type": "checklist", "criteria_label": "M\u1ee9c \u0111\u1ed9", "scale": [{"value": 1, "label": "Ch\u1ecdn", "kind": "checkbox"}], "criteria": ["R\u1ea5t nghi\u00eam tr\u1ecdng", "Nghi\u00eam tr\u1ecdng", "Trung b\u00ecnh", "Nh\u1eb9"]}','2026-07-01 05:15:21.849480','2026-07-01 05:15:21.849494',5,337,'question'),
 (7366,'B. YÊU CẦU ĐỐI VỚI HỆ THỐNG MỚI','',0,0,'[]','{}','{}','2026-07-01 05:15:21.865660','2026-07-01 05:15:21.865674',8,337,'question'),
 (7367,'1. Chức năng mong muốn','(1 = Không cần; 5 = Rất cần)',0,0,'[]','{}','{"grid_type": "scale5", "criteria_label": "Ch\u1ee9c n\u0103ng", "scale": [{"value": 1, "label": "1", "kind": "radio"}, {"value": 2, "label": "2", "kind": "radio"}, {"value": 3, "label": "3", "kind": "radio"}, {"value": 4, "label": "4", "kind": "radio"}, {"value": 5, "label": "5", "kind": "radio"}], "criteria": ["Qu\u1ea3n l\u00fd k\u1ebf ho\u1ea1ch CCHC", "Qu\u1ea3n l\u00fd nhi\u1ec7m v\u1ee5", "Qu\u1ea3n l\u00fd h\u1ed3 s\u01a1 minh ch\u1ee9ng \u0111i\u1ec7n t\u1eed", "T\u1ef1 \u0111\u1ed9ng t\u00ednh \u0111i\u1ec3m", "Dashboard \u0111i\u1ec1u h\u00e0nh", "T\u1ef1 \u0111\u1ed9ng t\u1ed5ng h\u1ee3p b\u00e1o c\u00e1o", "Qu\u1ea3n l\u00fd tr\u00ean Mobile", "T\u00edch h\u1ee3p LGSP", "T\u00edch h\u1ee3p SSO"]}','2026-07-01 05:15:21.883596','2026-07-01 05:15:21.883614',5,337,'question'),
 (7368,'2. Nhu cầu ứng dụng AI','',0,0,'[]','{}','{"grid_type": "yesno", "criteria_label": "Ti\u1ec7n \u00edch AI", "scale": [{"value": 1, "label": "C\u00f3 nhu c\u1ea7u", "kind": "radio"}, {"value": 2, "label": "Kh\u00f4ng", "kind": "radio"}], "criteria": ["AI h\u1ed7 tr\u1ee3 t\u00ecm ki\u1ebfm h\u1ed3 s\u01a1", "AI h\u1ed7 tr\u1ee3 t\u1ed5ng h\u1ee3p b\u00e1o c\u00e1o", "AI h\u1ed7 tr\u1ee3 ph\u00e2n t\u00edch d\u1eef li\u1ec7u CCHC", "AI c\u1ea3nh b\u00e1o r\u1ee7i ro", "AI Chatbot h\u1ed7 tr\u1ee3 ng\u01b0\u1eddi d\u00f9ng"]}','2026-07-01 05:15:21.897644','2026-07-01 05:15:21.897658',5,337,'question'),
 (7369,'1. Các hệ thống cần ưu tiên tích hợp','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 05:15:21.971882','2026-07-01 05:15:21.971896',2,338,'question'),
 (7370,'2. Các dữ liệu cần ưu tiên kế thừa','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 05:15:21.984530','2026-07-01 05:15:21.984543',2,338,'question'),
 (7371,'3. Các đề xuất khác','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 05:15:21.996801','2026-07-01 05:15:21.996813',2,338,'question'),
 (7522,'BM-06: Phiếu khảo sát hiện trạng dữ liệu','',0,0,'[]','{}','{}','2026-07-01 05:25:53.091772','2026-07-01 05:25:53.091785',8,339,'question'),
 (7523,'Thu thập thông tin về hiện trạng dữ liệu phục vụ công tác cải cách hành chính nhằm:','',0,0,'[]','{}','{}','2026-07-01 05:25:53.106222','2026-07-01 05:25:53.106253',9,339,'question'),
 (7524,'• Đánh giá hiện trạng dữ liệu đang quản lý.
• Xác định các nhóm dữ liệu phục vụ Hệ thống theo dõi, đánh giá CCHC.
• Đánh giá chất lượng dữ liệu.
• Đánh giá khả năng kế thừa dữ liệu.
• Xác định nhu cầu chuẩn hóa và chia sẻ dữ liệu.
• Làm cơ sở xây dựng mô hình dữ liệu của hệ thống.','',0,0,'[]','{}','{}','2026-07-01 05:25:53.119804','2026-07-01 05:25:53.119816',9,339,'question'),
 (7525,'Đơn vị:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 05:25:53.224276','2026-07-01 05:25:53.224289',1,340,'question'),
 (7526,'Người cung cấp:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 05:25:53.236523','2026-07-01 05:25:53.236536',1,340,'question'),
 (7527,'Chức vụ:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 05:25:53.249114','2026-07-01 05:25:53.249127',1,340,'question'),
 (7528,'Bộ phận:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 05:25:53.261400','2026-07-01 05:25:53.261417',1,340,'question'),
 (7529,'Điện thoại:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 05:25:53.310283','2026-07-01 05:25:53.310295',1,340,'question'),
 (7530,'Email:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 05:25:53.324624','2026-07-01 05:25:53.324641',1,340,'question'),
 (7531,'A. HIỆN TRẠNG DỮ LIỆU','',0,0,'[]','{}','{}','2026-07-01 05:25:53.588496','2026-07-01 05:25:53.588517',8,341,'question'),
 (7532,'1. Các nhóm dữ liệu hiện có','',0,0,'[]','{}','{"grid_type": "yesno", "criteria_label": "Nh\u00f3m d\u1eef li\u1ec7u", "scale": [{"value": 1, "label": "C\u00f3", "kind": "radio"}, {"value": 2, "label": "Kh\u00f4ng", "kind": "radio"}], "criteria": ["Danh m\u1ee5c c\u01a1 quan, \u0111\u01a1n v\u1ecb", "Danh m\u1ee5c x\u00e3, ph\u01b0\u1eddng", "Danh m\u1ee5c ng\u01b0\u1eddi d\u00f9ng", "K\u1ebf ho\u1ea1ch CCHC", "Nhi\u1ec7m v\u1ee5 CCHC", "H\u1ed3 s\u01a1 minh ch\u1ee9ng", "B\u1ed9 ti\u00eau ch\u00ed CCHC", "K\u1ebft qu\u1ea3 t\u1ef1 \u0111\u00e1nh gi\u00e1", "K\u1ebft qu\u1ea3 th\u1ea9m \u0111\u1ecbnh", "B\u00e1o c\u00e1o CCHC", "Nh\u1eadt k\u00fd x\u1eed l\u00fd", "Kh\u00e1c"]}','2026-07-01 05:25:53.606527','2026-07-01 05:25:53.606546',5,341,'question'),
 (7533,'2. Quy mô dữ liệu','',0,0,'[]','{}','{"columns": ["STT", "Nh\u00f3m d\u1eef li\u1ec7u", "S\u1ed1 l\u01b0\u1ee3ng b\u1ea3n ghi", "T\u0103ng tr\u01b0\u1edfng h\u00e0ng n\u0103m (%)"], "data": [["1", "K\u1ebf ho\u1ea1ch CCHC", "", ""], ["2", "Nhi\u1ec7m v\u1ee5 CCHC", "", ""], ["3", "H\u1ed3 s\u01a1 minh ch\u1ee9ng", "", ""], ["4", "B\u00e1o c\u00e1o", "", ""], ["5", "Ng\u01b0\u1eddi d\u00f9ng", "", ""], ["6", "H\u1ed3 s\u01a1 \u0111\u00e1nh gi\u00e1", "", ""]], "rows": 6}','2026-07-01 05:25:53.621786','2026-07-01 05:25:53.621804',6,341,'question'),
 (7534,'3. Hình thức lưu trữ','',0,0,'[]','{}','{"grid_type": "checklist", "criteria_label": "H\u00ecnh th\u1ee9c", "scale": [{"value": 1, "label": "C\u00f3", "kind": "checkbox"}], "criteria": ["Excel", "Word", "PDF", "SQL Server", "Oracle", "PostgreSQL", "MySQL", "MongoDB", "H\u1ec7 th\u1ed1ng Cloud", "Kh\u00e1c"]}','2026-07-01 05:25:53.635003','2026-07-01 05:25:53.635015',5,341,'question'),
 (7535,'4. Vị trí lưu trữ','',0,0,'[]','{}','{"grid_type": "checklist", "criteria_label": "N\u1ed9i dung", "scale": [{"value": 1, "label": "C\u00f3", "kind": "checkbox"}], "criteria": ["M\u00e1y t\u00ednh c\u00e1 nh\u00e2n", "M\u00e1y ch\u1ee7 n\u1ed9i b\u1ed9", "Trung t\u00e2m d\u1eef li\u1ec7u", "Cloud", "Nhi\u1ec1u n\u01a1i kh\u00e1c nhau"]}','2026-07-01 05:25:53.649282','2026-07-01 05:25:53.649302',5,341,'question'),
 (7536,'5. Đánh giá chất lượng dữ liệu','Đánh giá theo từng tiêu chí (1 = Rất kém; 5 = Rất tốt)',0,0,'[]','{}','{"grid_type": "scale5", "criteria_label": "Ti\u00eau ch\u00ed", "scale": [{"value": 1, "label": "1", "kind": "radio"}, {"value": 2, "label": "2", "kind": "radio"}, {"value": 3, "label": "3", "kind": "radio"}, {"value": 4, "label": "4", "kind": "radio"}, {"value": 5, "label": "5", "kind": "radio"}], "criteria": ["\u0110\u1ea7y \u0111\u1ee7", "Ch\u00ednh x\u00e1c", "\u0110\u1ed3ng nh\u1ea5t", "C\u1eadp nh\u1eadt k\u1ecbp th\u1eddi", "Kh\u00f4ng tr\u00f9ng l\u1eb7p", "D\u1ec5 khai th\u00e1c"]}','2026-07-01 05:25:53.663814','2026-07-01 05:25:53.663828',5,341,'question'),
 (7537,'6. Các vấn đề thường gặp','(Có thể chọn nhiều)',0,0,'["Thi\u1ebfu d\u1eef li\u1ec7u", "Sai d\u1eef li\u1ec7u", "D\u1eef li\u1ec7u tr\u00f9ng l\u1eb7p", "Kh\u00f4ng \u0111\u1ed3ng nh\u1ea5t", "Thi\u1ebfu m\u00e3 \u0111\u1ecbnh danh", "Kh\u00f3 t\u00ecm ki\u1ebfm", "Kh\u00f3 t\u1ed5ng h\u1ee3p", "Kh\u00f4ng c\u00f3 l\u1ecbch s\u1eed thay \u0111\u1ed5i", "Kh\u00e1c"]','{}','{"options": ["Thi\u1ebfu d\u1eef li\u1ec7u", "Sai d\u1eef li\u1ec7u", "D\u1eef li\u1ec7u tr\u00f9ng l\u1eb7p", "Kh\u00f4ng \u0111\u1ed3ng nh\u1ea5t", "Thi\u1ebfu m\u00e3 \u0111\u1ecbnh danh", "Kh\u00f3 t\u00ecm ki\u1ebfm", "Kh\u00f3 t\u1ed5ng h\u1ee3p", "Kh\u00f4ng c\u00f3 l\u1ecbch s\u1eed thay \u0111\u1ed5i", "Kh\u00e1c"]}','2026-07-01 05:25:53.677523','2026-07-01 05:25:53.677535',4,341,'question'),
 (7538,'7.  Khảo sát danh mục dữ liệu dùng chung','',0,0,'[]','{}','{}','2026-07-01 05:25:53.690040','2026-07-01 05:25:53.690053',8,341,'question'),
 (7539,'a. Các danh mục đang sử dụng','',0,0,'[]','{}','{"grid_type": "checklist", "criteria_label": "Danh m\u1ee5c", "scale": [{"value": 1, "label": "C\u00f3", "kind": "checkbox"}], "criteria": ["Danh m\u1ee5c \u0111\u01a1n v\u1ecb", "Danh m\u1ee5c ti\u00eau ch\u00ed CCHC", "Danh m\u1ee5c nhi\u1ec7m v\u1ee5", "Danh m\u1ee5c lo\u1ea1i minh ch\u1ee9ng", "Danh m\u1ee5c tr\u1ea1ng th\u00e1i", "Danh m\u1ee5c ng\u01b0\u1eddi d\u00f9ng", "Kh\u00e1c"]}','2026-07-01 05:25:53.702702','2026-07-01 05:25:53.702715',5,341,'question'),
 (7540,'b. Mức độ chuẩn hóa','',0,0,'[]','{}','{"grid_type": "yesno", "criteria_label": "Ti\u00eau ch\u00ed", "scale": [{"value": 1, "label": "C\u00f3", "kind": "radio"}, {"value": 2, "label": "Kh\u00f4ng", "kind": "radio"}], "criteria": ["C\u00f3 m\u00e3 \u0111\u1ecbnh danh", "C\u00f3 quy t\u1eafc \u0111\u1eb7t t\u00ean", "C\u00f3 qu\u1ea3n l\u00fd phi\u00ean b\u1ea3n", "C\u00f3 d\u1eef li\u1ec7u d\u00f9ng chung"]}','2026-07-01 05:25:53.715393','2026-07-01 05:25:53.715406',5,341,'question'),
 (7541,'8. Khả năng kế thừa dữ liệu','',0,0,'[]','{}','{}','2026-07-01 05:25:53.727962','2026-07-01 05:25:53.727974',8,341,'question'),
 (7542,'a. Dữ liệu cần chuyển sang hệ thống mới','',0,0,'[]','{}','{"grid_type": "yesno", "criteria_label": "Nh\u00f3m d\u1eef li\u1ec7u", "scale": [{"value": 1, "label": "C\u00f3", "kind": "radio"}, {"value": 2, "label": "Kh\u00f4ng", "kind": "radio"}], "criteria": ["Danh m\u1ee5c \u0111\u01a1n v\u1ecb", "Ng\u01b0\u1eddi d\u00f9ng", "K\u1ebf ho\u1ea1ch CCHC", "Nhi\u1ec7m v\u1ee5", "H\u1ed3 s\u01a1 minh ch\u1ee9ng", "K\u1ebft qu\u1ea3 \u0111\u00e1nh gi\u00e1", "B\u00e1o c\u00e1o"]}','2026-07-01 05:25:53.740327','2026-07-01 05:25:53.740341',5,341,'question'),
 (7543,'b. Đánh giá khả năng chuyển đổi','',0,0,'[]','{}','{"grid_type": "yesno", "criteria_label": "Ti\u00eau ch\u00ed", "scale": [{"value": 1, "label": "C\u00f3", "kind": "radio"}, {"value": 2, "label": "Kh\u00f4ng", "kind": "radio"}], "criteria": ["C\u00f3 th\u1ec3 xu\u1ea5t Excel", "C\u00f3 API", "C\u00f3 Database", "C\u00f3 t\u00e0i li\u1ec7u d\u1eef li\u1ec7u"]}','2026-07-01 05:25:53.752556','2026-07-01 05:25:53.752567',5,341,'question'),
 (7544,'9. Khảo sát chia sẻ và tích hợp dữ liệu','',0,0,'[]','{}','{}','2026-07-01 05:25:53.766006','2026-07-01 05:25:53.766020',8,341,'question'),
 (7545,'a. Dữ liệu cần chia sẻ','',0,0,'[]','{}','{"grid_type": "yesno", "criteria_label": "D\u1eef li\u1ec7u", "scale": [{"value": 1, "label": "C\u1ea7n", "kind": "radio"}, {"value": 2, "label": "Kh\u00f4ng", "kind": "radio"}], "criteria": ["Danh m\u1ee5c \u0111\u01a1n v\u1ecb", "K\u1ebft qu\u1ea3 CCHC", "H\u1ed3 s\u01a1 minh ch\u1ee9ng", "B\u00e1o c\u00e1o", "Dashboard"]}','2026-07-01 05:25:53.778334','2026-07-01 05:25:53.778347',5,341,'question'),
 (7546,'b. Hệ thống cần chia sẻ dữ liệu','',0,0,'[]','{}','{"grid_type": "checklist", "criteria_label": "H\u1ec7 th\u1ed1ng", "scale": [{"value": 1, "label": "C\u00f3", "kind": "checkbox"}], "criteria": ["N\u1ec1n t\u1ea3ng LGSP", "Kho d\u1eef li\u1ec7u d\u00f9ng chung", "H\u1ec7 th\u1ed1ng b\u00e1o c\u00e1o", "H\u1ec7 th\u1ed1ng qu\u1ea3n l\u00fd v\u0103n b\u1ea3n", "H\u1ec7 th\u1ed1ng x\u00e1c th\u1ef1c SSO", "Kh\u00e1c"]}','2026-07-01 05:25:53.790432','2026-07-01 05:25:53.790445',5,341,'question'),
 (7547,'B. NHU CẦU QUẢN LÝ DỮ LIỆU','(1 = Không cần; 5 = Rất cần)',0,0,'[]','{}','{"grid_type": "scale5", "criteria_label": "Ch\u1ee9c n\u0103ng", "scale": [{"value": 1, "label": "1", "kind": "radio"}, {"value": 2, "label": "2", "kind": "radio"}, {"value": 3, "label": "3", "kind": "radio"}, {"value": 4, "label": "4", "kind": "radio"}, {"value": 5, "label": "5", "kind": "radio"}], "criteria": ["Chu\u1ea9n h\u00f3a d\u1eef li\u1ec7u", "Qu\u1ea3n l\u00fd danh m\u1ee5c d\u00f9ng chung", "Qu\u1ea3n l\u00fd Metadata", "Ki\u1ec3m tra ch\u1ea5t l\u01b0\u1ee3ng d\u1eef li\u1ec7u", "\u0110\u1ed3ng b\u1ed9 d\u1eef li\u1ec7u t\u1ef1 \u0111\u1ed9ng", "Theo d\u00f5i l\u1ecbch s\u1eed thay \u0111\u1ed5i"]}','2026-07-01 05:25:53.802036','2026-07-01 05:25:53.802049',5,341,'question'),
 (7548,'1. Theo đơn vị, những nhóm dữ liệu nào cần ưu tiên số hóa?','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 05:25:53.882680','2026-07-01 05:25:53.882695',2,342,'question'),
 (7549,'2. Những dữ liệu nào cần chuẩn hóa trước khi đưa vào hệ thống?','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 05:25:53.896854','2026-07-01 05:25:53.896867',2,342,'question'),
 (7550,'3. Những dữ liệu nào cần chia sẻ giữa các đơn vị?','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 05:25:53.908917','2026-07-01 05:25:53.908929',2,342,'question'),
 (7551,'4. Các đề xuất khác','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 05:25:53.921384','2026-07-01 05:25:53.921400',2,342,'question'),
 (7776,'BM-07: Phiếu khảo sát hạ tầng kỹ thuật và An toàn thông tin','',0,0,'[]','{}','{}','2026-07-01 06:08:53.495277','2026-07-01 06:08:53.495290',8,343,'question'),
 (7777,'Thu thập thông tin về hiện trạng hạ tầng công nghệ thông tin, hạ tầng mạng, trung tâm dữ liệu, thiết bị đầu cuối, môi trường triển khai và công tác bảo đảm an toàn thông tin nhằm:','',0,0,'[]','{}','{}','2026-07-01 06:08:53.508453','2026-07-01 06:08:53.508465',9,343,'question'),
 (7778,'• Đánh giá mức độ sẵn sàng triển khai hệ thống.
• Xác định khả năng tận dụng hạ tầng hiện có.
• Xác định nhu cầu đầu tư, nâng cấp hạ tầng.
• Làm cơ sở thiết kế kiến trúc triển khai hệ thống.
• Xây dựng phương án bảo đảm an toàn thông tin theo quy định.','',0,0,'[]','{}','{}','2026-07-01 06:08:53.521883','2026-07-01 06:08:53.521895',9,343,'question'),
 (7779,'Đơn vị:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 06:08:53.622343','2026-07-01 06:08:53.622357',1,344,'question'),
 (7780,'Người cung cấp:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 06:08:53.634915','2026-07-01 06:08:53.634932',1,344,'question'),
 (7781,'Chức vụ:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 06:08:53.647400','2026-07-01 06:08:53.647414',1,344,'question'),
 (7782,'Bộ phận:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 06:08:53.660085','2026-07-01 06:08:53.660099',1,344,'question'),
 (7783,'Điện thoại:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 06:08:53.673219','2026-07-01 06:08:53.673233',1,344,'question'),
 (7784,'Email:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 06:08:53.685621','2026-07-01 06:08:53.685636',1,344,'question'),
 (7785,'1. Hạ tầng trung tâm dữ liệu','',0,0,'[]','{}','{}','2026-07-01 06:08:54.015969','2026-07-01 06:08:54.015983',8,345,'question'),
 (7786,'a. Mô hình triển khai hiện nay','Đơn vị hiện đang triển khai các hệ thống CNTT theo mô hình nào?',0,0,'[]','{}','{"grid_type": "checklist", "criteria_label": "M\u00f4 h\u00ecnh", "scale": [{"value": 1, "label": "Ch\u1ecdn", "kind": "checkbox"}], "criteria": ["Trung t\u00e2m d\u1eef li\u1ec7u Th\u00e0nh ph\u1ed1", "Trung t\u00e2m d\u1eef li\u1ec7u c\u1ee7a \u0111\u01a1n v\u1ecb", "\u0110i\u1ec7n to\u00e1n \u0111\u00e1m m\u00e2y (Cloud)", "K\u1ebft h\u1ee3p On-premise v\u00e0 Cloud", "Kh\u00e1c"]}','2026-07-01 06:08:54.028322','2026-07-01 06:08:54.028336',5,345,'question'),
 (7787,'b. Máy chủ hiện có','',0,0,'[]','{}','{"columns": ["STT", "M\u00e1y ch\u1ee7", "S\u1ed1 l\u01b0\u1ee3ng", "CPU", "RAM", "Storage", "Ghi ch\u00fa"], "data": [["1", "Application Server", "", "", "", "", ""], ["2", "Database Server", "", "", "", "", ""], ["3", "File Server", "", "", "", "", ""], ["4", "Backup Server", "", "", "", "", ""]], "rows": 4}','2026-07-01 06:08:54.041919','2026-07-01 06:08:54.041933',6,345,'question'),
 (7788,'c. Hệ thống lưu trữ','',0,0,'[]','{}','{"grid_type": "yesno", "criteria_label": "N\u1ed9i dung", "scale": [{"value": 1, "label": "C\u00f3", "kind": "radio"}, {"value": 2, "label": "Kh\u00f4ng", "kind": "radio"}], "criteria": ["SAN Storage", "NAS Storage", "Object Storage", "Cloud Storage", "Kh\u00e1c"]}','2026-07-01 06:08:54.054646','2026-07-01 06:08:54.054661',5,345,'question'),
 (7789,'Dung lượng lưu trữ hiện tại: __________ TB','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 06:08:54.067687','2026-07-01 06:08:54.067706',1,345,'question'),
 (7790,'Dung lượng còn trống: __________ TB','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 06:08:54.079981','2026-07-01 06:08:54.079994',1,345,'question'),
 (7791,'2. Hạ tầng mạng','',0,0,'[]','{}','{}','2026-07-01 06:08:54.092600','2026-07-01 06:08:54.092616',8,345,'question'),
 (7792,'a. Kết nối mạng','',0,0,'[]','{}','{"grid_type": "checklist", "criteria_label": "N\u1ed9i dung", "scale": [{"value": 1, "label": "C\u00f3", "kind": "checkbox"}], "criteria": ["M\u1ea1ng truy\u1ec1n s\u1ed1 li\u1ec7u chuy\u00ean d\u00f9ng", "Internet", "MPLS VPN", "SD-WAN"]}','2026-07-01 06:08:54.105352','2026-07-01 06:08:54.105363',5,345,'question'),
 (7793,'b. Thiết bị mạng','',0,0,'[]','{}','{"columns": ["Thi\u1ebft b\u1ecb", "S\u1ed1 l\u01b0\u1ee3ng"], "data": [["Router", ""], ["Switch", ""], ["Firewall", ""], ["IDS/IPS", ""], ["Load Balancer", ""], ["Wifi Controller", ""]], "rows": 6}','2026-07-01 06:08:54.117618','2026-07-01 06:08:54.117632',6,345,'question'),
 (7794,'c. Đánh giá chất lượng mạng','(1 = Rất kém; 5 = Rất tốt)',0,0,'[]','{}','{"grid_type": "scale5", "criteria_label": "Ti\u00eau ch\u00ed", "scale": [{"value": 1, "label": "1", "kind": "radio"}, {"value": 2, "label": "2", "kind": "radio"}, {"value": 3, "label": "3", "kind": "radio"}, {"value": 4, "label": "4", "kind": "radio"}, {"value": 5, "label": "5", "kind": "radio"}], "criteria": ["B\u0103ng th\u00f4ng", "\u0110\u1ed9 \u1ed5n \u0111\u1ecbnh", "\u0110\u1ed9 tr\u1ec5", "Kh\u1ea3 n\u0103ng m\u1edf r\u1ed9ng"]}','2026-07-01 06:08:54.129716','2026-07-01 06:08:54.129729',5,345,'question'),
 (7795,'3. THIẾT BỊ ĐẦU CUỐI','',0,0,'[]','{}','{}','2026-07-01 06:08:54.141687','2026-07-01 06:08:54.141700',8,345,'question'),
 (7796,'a. Máy trạm','',0,0,'[]','{}','{"columns": ["Thi\u1ebft b\u1ecb", "S\u1ed1 l\u01b0\u1ee3ng"], "data": [["Desktop", ""], ["Laptop", ""], ["Thin Client", ""]], "rows": 3}','2026-07-01 06:08:54.154171','2026-07-01 06:08:54.154189',6,345,'question'),
 (7797,'b. Hệ điều hành','',0,0,'[]','{}','{"columns": ["H\u1ec7 \u0111i\u1ec1u h\u00e0nh", "S\u1ed1 l\u01b0\u1ee3ng"], "data": [["Windows 10", ""], ["Windows 11", ""], ["Linux", ""], ["Kh\u00e1c", ""]], "rows": 4}','2026-07-01 06:08:54.168471','2026-07-01 06:08:54.168484',6,345,'question'),
 (7798,'c. Trình duyệt','',0,0,'[]','{}','{"grid_type": "checklist", "criteria_label": "Tr\u00ecnh duy\u1ec7t", "scale": [{"value": 1, "label": "C\u00f3 s\u1eed d\u1ee5ng", "kind": "checkbox"}], "criteria": ["Chrome", "Edge", "Firefox", "Safari"]}','2026-07-01 06:08:54.181161','2026-07-01 06:08:54.181174',5,345,'question'),
 (7799,'d. Thiết bị di động','',0,0,'[]','{}','{"grid_type": "checklist", "criteria_label": "Thi\u1ebft b\u1ecb", "scale": [{"value": 1, "label": "C\u00f3", "kind": "checkbox"}], "criteria": ["Android", "iPhone", "Tablet"]}','2026-07-01 06:08:54.193174','2026-07-01 06:08:54.193187',5,345,'question'),
 (7800,'e. Có nhu cầu sử dụng hệ thống trên thiết bị di động?','',0,0,'["C\u00f3", "Kh\u00f4ng"]','{}','{"options": ["C\u00f3", "Kh\u00f4ng"]}','2026-07-01 06:08:54.206004','2026-07-01 06:08:54.206021',3,345,'question'),
 (7801,'4. Hiện trạng an toàn thông tin','',0,0,'[]','{}','{}','2026-07-01 06:08:54.220332','2026-07-01 06:08:54.220346',8,345,'question'),
 (7802,'a. Quản lý tài khoản','',0,0,'[]','{}','{"grid_type": "checklist", "criteria_label": "N\u1ed9i dung", "scale": [{"value": 1, "label": "C\u00f3", "kind": "checkbox"}], "criteria": ["Active Directory", "LDAP", "SSO", "VNeID"]}','2026-07-01 06:08:54.233972','2026-07-01 06:08:54.233988',5,345,'question'),
 (7803,'b. Phân quyền','',0,0,'[]','{}','{"grid_type": "checklist", "criteria_label": "N\u1ed9i dung", "scale": [{"value": 1, "label": "C\u00f3", "kind": "checkbox"}], "criteria": ["Ph\u00e2n quy\u1ec1n theo vai tr\u00f2", "Ph\u00e2n quy\u1ec1n theo \u0111\u01a1n v\u1ecb", "Ph\u00e2n quy\u1ec1n theo ch\u1ee9c n\u0103ng"]}','2026-07-01 06:08:54.247572','2026-07-01 06:08:54.247584',5,345,'question'),
 (7804,'c. Nhật ký hệ thống','',0,0,'[]','{}','{"grid_type": "checklist", "criteria_label": "N\u1ed9i dung", "scale": [{"value": 1, "label": "C\u00f3", "kind": "checkbox"}], "criteria": ["Audit Log", "Theo d\u00f5i \u0111\u0103ng nh\u1eadp", "Theo d\u00f5i thao t\u00e1c", "Theo d\u00f5i thay \u0111\u1ed5i d\u1eef li\u1ec7u"]}','2026-07-01 06:08:54.261321','2026-07-01 06:08:54.261334',5,345,'question'),
 (7805,'d. Bảo vệ hệ thống','',0,0,'[]','{}','{"grid_type": "checklist", "criteria_label": "N\u1ed9i dung", "scale": [{"value": 1, "label": "C\u00f3", "kind": "checkbox"}], "criteria": ["Firewall", "WAF", "Antivirus", "EDR/XDR", "IPS/IDS", "MFA", "M\u00e3 h\u00f3a d\u1eef li\u1ec7u"]}','2026-07-01 06:08:54.275500','2026-07-01 06:08:54.275515',5,345,'question'),
 (7806,'e. Sao lưu dữ liệu','',0,0,'[]','{}','{"grid_type": "checklist", "criteria_label": "N\u1ed9i dung", "scale": [{"value": 1, "label": "C\u00f3", "kind": "checkbox"}], "criteria": ["Backup h\u1eb1ng ng\u00e0y", "Backup \u0111\u1ecbnh k\u1ef3", "Backup Offsite", "Kh\u00f4i ph\u1ee5c th\u1eed nghi\u1ec7m"]}','2026-07-01 06:08:54.291908','2026-07-01 06:08:54.291920',5,345,'question'),
 (7807,'g. Đánh giá cấp độ ATTT','Đơn vị đã được phê duyệt cấp độ ATTT chưa?',0,0,'["Ch\u01b0a", "C\u1ea5p \u0111\u1ed9 1", "C\u1ea5p \u0111\u1ed9 2", "C\u1ea5p \u0111\u1ed9 3", "C\u1ea5p \u0111\u1ed9 4", "C\u1ea5p \u0111\u1ed9 5"]','{}','{"options": ["Ch\u01b0a", "C\u1ea5p \u0111\u1ed9 1", "C\u1ea5p \u0111\u1ed9 2", "C\u1ea5p \u0111\u1ed9 3", "C\u1ea5p \u0111\u1ed9 4", "C\u1ea5p \u0111\u1ed9 5"]}','2026-07-01 06:08:54.306125','2026-07-01 06:08:54.306139',4,345,'question'),
 (7808,'B. NHU CẦU TRIỂN KHAI HỆ THỐNG MỚI','',0,0,'[]','{}','{}','2026-07-01 06:08:54.320369','2026-07-01 06:08:54.320383',8,345,'question'),
 (7809,'Mô hình mong muốn','',0,0,'[]','{}','{"grid_type": "checklist", "criteria_label": "M\u00f4 h\u00ecnh", "scale": [{"value": 1, "label": "Ch\u1ecdn", "kind": "checkbox"}], "criteria": ["Tri\u1ec3n khai t\u1ea1i Trung t\u00e2m d\u1eef li\u1ec7u Th\u00e0nh ph\u1ed1", "Cloud", "Hybrid Cloud", "Ch\u01b0a x\u00e1c \u0111\u1ecbnh"]}','2026-07-01 06:08:54.334122','2026-07-01 06:08:54.334135',5,345,'question'),
 (7810,'1. Theo đơn vị, hạ tầng hiện tại còn thiếu những gì?','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 06:08:54.400407','2026-07-01 06:08:54.400437',2,346,'question'),
 (7811,'2. Những yêu cầu về ATTT cần ưu tiên','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 06:08:54.414830','2026-07-01 06:08:54.414848',2,346,'question'),
 (7812,'3. Những đề xuất khác','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 06:08:54.427482','2026-07-01 06:08:54.427500',2,346,'question'),
 (7873,'BM-08: Phiếu khảo sát nhu cầu Dashboard và báo cáo','',0,0,'[]','{}','{}','2026-07-01 06:14:26.109946','2026-07-01 06:14:26.109959',8,347,'question'),
 (7874,'Thu thập yêu cầu của các cơ quan, đơn vị về:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 06:14:26.122771','2026-07-01 06:14:26.122783',1,347,'question'),
 (7875,'• Các báo cáo phục vụ công tác quản lý, điều hành.
• Các Dashboard phục vụ lãnh đạo các cấp.
• Các chỉ số (KPI) cần theo dõi.
• Các hình thức trực quan hóa dữ liệu.
• Nhu cầu khai thác dữ liệu, cảnh báo và phân tích.','',0,0,'[]','{}','{}','2026-07-01 06:14:26.135351','2026-07-01 06:14:26.135370',9,347,'question'),
 (7876,'Đơn vị:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 06:14:26.237619','2026-07-01 06:14:26.237640',1,348,'question'),
 (7877,'Người cung cấp:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 06:14:26.249705','2026-07-01 06:14:26.249719',1,348,'question'),
 (7878,'Chức vụ:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 06:14:26.261299','2026-07-01 06:14:26.261315',1,348,'question'),
 (7879,'Bộ phận:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 06:14:26.273385','2026-07-01 06:14:26.273407',1,348,'question'),
 (7880,'Điện thoại:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 06:14:26.285252','2026-07-01 06:14:26.285264',1,348,'question'),
 (7881,'Email:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 06:14:26.298110','2026-07-01 06:14:26.298126',1,348,'question'),
 (7882,'1. Mục đích sử dụng Dashboard','Đơn vị sử dụng Dashboard để phục vụ mục đích nào? (Có thể chọn nhiều)',0,0,'["Theo d\u00f5i ti\u1ebfn \u0111\u1ed9 CCHC", "\u0110i\u1ec1u h\u00e0nh c\u00f4ng vi\u1ec7c", "Ki\u1ec3m tra t\u00ecnh h\u00ecnh th\u1ef1c hi\u1ec7n", "Ph\u00e2n t\u00edch d\u1eef li\u1ec7u", "H\u1ecdp giao ban", "B\u00e1o c\u00e1o l\u00e3nh \u0111\u1ea1o", "C\u00f4ng khai k\u1ebft qu\u1ea3", "Kh\u00e1c:"]','{}','{"options": ["Theo d\u00f5i ti\u1ebfn \u0111\u1ed9 CCHC", "\u0110i\u1ec1u h\u00e0nh c\u00f4ng vi\u1ec7c", "Ki\u1ec3m tra t\u00ecnh h\u00ecnh th\u1ef1c hi\u1ec7n", "Ph\u00e2n t\u00edch d\u1eef li\u1ec7u", "H\u1ecdp giao ban", "B\u00e1o c\u00e1o l\u00e3nh \u0111\u1ea1o", "C\u00f4ng khai k\u1ebft qu\u1ea3", "Kh\u00e1c:"]}','2026-07-01 06:14:26.558161','2026-07-01 06:14:26.558173',4,349,'question'),
 (7883,'2. Tần suất sử dụng','',0,0,'[]','{}','{"grid_type": "checklist", "criteria_label": "T\u1ea7n su\u1ea5t", "scale": [{"value": 1, "label": "Ch\u1ecdn", "kind": "checkbox"}], "criteria": ["H\u00e0ng ng\u00e0y", "H\u00e0ng tu\u1ea7n", "H\u00e0ng th\u00e1ng", "H\u00e0ng qu\u00fd", "Khi c\u1ea7n"]}','2026-07-01 06:14:26.573087','2026-07-01 06:14:26.573099',5,349,'question'),
 (7884,'3. Nhu cầu về các loại Dashboard','',0,0,'[]','{}','{}','2026-07-01 06:14:26.587773','2026-07-01 06:14:26.587787',8,349,'question'),
 (7885,'a. Dashboard tổng thể','Đánh giá mức độ cần thiết (1 = Không cần; 5 = Rất cần)',0,0,'[]','{}','{"grid_type": "scale5", "criteria_label": "Dashboard", "scale": [{"value": 1, "label": "1", "kind": "radio"}, {"value": 2, "label": "2", "kind": "radio"}, {"value": 3, "label": "3", "kind": "radio"}, {"value": 4, "label": "4", "kind": "radio"}, {"value": 5, "label": "5", "kind": "radio"}], "criteria": ["Dashboard t\u1ed5ng th\u1ec3 CCHC to\u00e0n Th\u00e0nh ph\u1ed1", "Dashboard theo S\u1edf, ban, ng\u00e0nh", "Dashboard theo x\u00e3, ph\u01b0\u1eddng", "Dashboard theo l\u0129nh v\u1ef1c CCHC"]}','2026-07-01 06:14:26.604638','2026-07-01 06:14:26.604652',5,349,'question'),
 (7886,'b. Dashboard điều hành','',0,0,'[]','{}','{"grid_type": "scale5", "criteria_label": "Dashboard", "scale": [{"value": 1, "label": "1", "kind": "radio"}, {"value": 2, "label": "2", "kind": "radio"}, {"value": 3, "label": "3", "kind": "radio"}, {"value": 4, "label": "4", "kind": "radio"}, {"value": 5, "label": "5", "kind": "radio"}], "criteria": ["Ti\u1ebfn \u0111\u1ed9 th\u1ef1c hi\u1ec7n nhi\u1ec7m v\u1ee5", "T\u1ef7 l\u1ec7 ho\u00e0n th\u00e0nh nhi\u1ec7m v\u1ee5", "Nhi\u1ec7m v\u1ee5 qu\u00e1 h\u1ea1n", "H\u1ed3 s\u01a1 minh ch\u1ee9ng", "Ti\u1ebfn \u0111\u1ed9 n\u1ed9p minh ch\u1ee9ng", "K\u1ebft qu\u1ea3 t\u1ef1 \u0111\u00e1nh gi\u00e1", "K\u1ebft qu\u1ea3 th\u1ea9m \u0111\u1ecbnh", "X\u1ebfp h\u1ea1ng CCHC"]}','2026-07-01 06:14:26.619034','2026-07-01 06:14:26.619047',5,349,'question'),
 (7887,'c. Dashboard phân tích','',0,0,'[]','{}','{"grid_type": "scale5", "criteria_label": "Dashboard", "scale": [{"value": 1, "label": "1", "kind": "radio"}, {"value": 2, "label": "2", "kind": "radio"}, {"value": 3, "label": "3", "kind": "radio"}, {"value": 4, "label": "4", "kind": "radio"}, {"value": 5, "label": "5", "kind": "radio"}], "criteria": ["So s\u00e1nh gi\u1eefa c\u00e1c \u0111\u01a1n v\u1ecb", "So s\u00e1nh gi\u1eefa c\u00e1c k\u1ef3 \u0111\u00e1nh gi\u00e1", "Xu h\u01b0\u1edbng c\u1ea3i thi\u1ec7n CCHC", "Ph\u00e2n t\u00edch theo ti\u00eau ch\u00ed", "Ph\u00e2n t\u00edch theo \u0111\u1ecba b\u00e0n", "Ph\u00e2n t\u00edch theo th\u1eddi gian"]}','2026-07-01 06:14:26.631323','2026-07-01 06:14:26.631335',5,349,'question'),
 (7888,'4. Nhu cầu KPI','',0,0,'[]','{}','{}','2026-07-01 06:14:26.643730','2026-07-01 06:14:26.643742',8,349,'question'),
 (7889,'Đánh giá mức độ cần thiết của các KPI','',0,0,'[]','{}','{"grid_type": "scale5", "criteria_label": "KPI", "scale": [{"value": 1, "label": "1", "kind": "radio"}, {"value": 2, "label": "2", "kind": "radio"}, {"value": 3, "label": "3", "kind": "radio"}, {"value": 4, "label": "4", "kind": "radio"}, {"value": 5, "label": "5", "kind": "radio"}], "criteria": ["T\u1ef7 l\u1ec7 ho\u00e0n th\u00e0nh k\u1ebf ho\u1ea1ch CCHC", "T\u1ef7 l\u1ec7 ho\u00e0n th\u00e0nh nhi\u1ec7m v\u1ee5", "T\u1ef7 l\u1ec7 nhi\u1ec7m v\u1ee5 \u0111\u00fang h\u1ea1n", "T\u1ef7 l\u1ec7 nhi\u1ec7m v\u1ee5 qu\u00e1 h\u1ea1n", "T\u1ef7 l\u1ec7 n\u1ed9p minh ch\u1ee9ng \u0111\u00fang h\u1ea1n", "\u0110i\u1ec3m CCHC trung b\u00ecnh", "X\u1ebfp h\u1ea1ng CCHC", "M\u1ee9c \u0111\u1ed9 c\u1ea3i thi\u1ec7n qua c\u00e1c n\u0103m"]}','2026-07-01 06:14:26.657532','2026-07-01 06:14:26.657547',5,349,'question'),
 (7890,'5. Nhu cầu báo cáo','',0,0,'[]','{}','{}','2026-07-01 06:14:26.670296','2026-07-01 06:14:26.670314',8,349,'question'),
 (7891,'a. Các báo cáo cần khai thác','',0,0,'[]','{}','{"grid_type": "yesno", "criteria_label": "B\u00e1o c\u00e1o", "scale": [{"value": 1, "label": "C\u1ea7n", "kind": "radio"}, {"value": 2, "label": "Kh\u00f4ng", "kind": "radio"}], "criteria": ["B\u00e1o c\u00e1o t\u1ed5ng h\u1ee3p CCHC", "B\u00e1o c\u00e1o ti\u1ebfn \u0111\u1ed9 nhi\u1ec7m v\u1ee5", "B\u00e1o c\u00e1o h\u1ed3 s\u01a1 minh ch\u1ee9ng", "B\u00e1o c\u00e1o k\u1ebft qu\u1ea3 ch\u1ea5m \u0111i\u1ec3m", "B\u00e1o c\u00e1o x\u1ebfp h\u1ea1ng", "B\u00e1o c\u00e1o theo ti\u00eau ch\u00ed", "B\u00e1o c\u00e1o theo \u0111\u1ecba b\u00e0n", "B\u00e1o c\u00e1o th\u1ed1ng k\u00ea ng\u01b0\u1eddi d\u00f9ng"]}','2026-07-01 06:14:26.683181','2026-07-01 06:14:26.683194',5,349,'question'),
 (7892,'b. Chu kỳ báo cáo','',0,0,'[]','{}','{"grid_type": "checklist", "criteria_label": "Chu k\u1ef3", "scale": [{"value": 1, "label": "C\u00f3", "kind": "checkbox"}], "criteria": ["Theo ng\u00e0y", "Theo tu\u1ea7n", "Theo th\u00e1ng", "Theo qu\u00fd", "Theo n\u0103m", "Theo k\u1ef3 \u0111\u00e1nh gi\u00e1", "Theo y\u00eau c\u1ea7u"]}','2026-07-01 06:14:26.695125','2026-07-01 06:14:26.695137',5,349,'question'),
 (7893,'c. Hình thức xuất báo cáo','',0,0,'[]','{}','{"grid_type": "checklist", "criteria_label": "\u0110\u1ecbnh d\u1ea1ng", "scale": [{"value": 1, "label": "C\u00f3", "kind": "checkbox"}], "criteria": ["PDF", "Word", "Excel", "Power BI", "Dashboard Web"]}','2026-07-01 06:14:26.707513','2026-07-01 06:14:26.707524',5,349,'question'),
 (7894,'6. Nhu cầu cảnh báo','',0,0,'[]','{}','{}','2026-07-01 06:14:26.722284','2026-07-01 06:14:26.722297',8,349,'question'),
 (7895,'a. Đơn vị có nhu cầu nhận cảnh báo đối với các nội dung sau không?','',0,0,'[]','{}','{"grid_type": "yesno", "criteria_label": "N\u1ed9i dung", "scale": [{"value": 1, "label": "C\u00f3", "kind": "radio"}, {"value": 2, "label": "Kh\u00f4ng", "kind": "radio"}], "criteria": ["Nhi\u1ec7m v\u1ee5 s\u1eafp qu\u00e1 h\u1ea1n", "Nhi\u1ec7m v\u1ee5 qu\u00e1 h\u1ea1n", "Ch\u01b0a n\u1ed9p minh ch\u1ee9ng", "Thi\u1ebfu h\u1ed3 s\u01a1", "\u0110i\u1ec3m CCHC th\u1ea5p", "Ch\u01b0a ho\u00e0n th\u00e0nh k\u1ebf ho\u1ea1ch"]}','2026-07-01 06:14:26.736091','2026-07-01 06:14:26.736103',5,349,'question'),
 (7896,'b. Hình thức nhận cảnh báo','',0,0,'["Email", "SMS", "Th\u00f4ng b\u00e1o tr\u00ean h\u1ec7 th\u1ed1ng", "\u1ee8ng d\u1ee5ng Mobile", "Microsoft Teams/Zalo (n\u1ebfu c\u00f3)"]','{}','{"options": ["Email", "SMS", "Th\u00f4ng b\u00e1o tr\u00ean h\u1ec7 th\u1ed1ng", "\u1ee8ng d\u1ee5ng Mobile", "Microsoft Teams/Zalo (n\u1ebfu c\u00f3)"]}','2026-07-01 06:14:26.749079','2026-07-01 06:14:26.749092',4,349,'question'),
 (7897,'7. Nhu cầu phân tích dữ liệu','Đơn vị có nhu cầu sử dụng các chức năng phân tích sau không?',0,0,'[]','{}','{"grid_type": "yesno", "criteria_label": "N\u1ed9i dung", "scale": [{"value": 1, "label": "C\u00f3", "kind": "radio"}, {"value": 2, "label": "Kh\u00f4ng", "kind": "radio"}], "criteria": ["So s\u00e1nh nhi\u1ec1u n\u0103m", "So s\u00e1nh gi\u1eefa c\u00e1c \u0111\u01a1n v\u1ecb", "Ph\u00e2n t\u00edch xu h\u01b0\u1edbng", "Ph\u00e2n t\u00edch theo ti\u00eau ch\u00ed", "Ph\u00e2n t\u00edch theo \u0111\u1ecba b\u00e0n", "Ph\u00e2n t\u00edch nguy\u00ean nh\u00e2n gi\u1ea3m \u0111i\u1ec3m"]}','2026-07-01 06:14:26.761609','2026-07-01 06:14:26.761627',5,349,'question'),
 (7898,'8. Nhu cầu AI và phân tích thông minh','Đánh giá mức độ cần thiết',0,0,'[]','{}','{"grid_type": "scale5", "criteria_label": "Ti\u1ec7n \u00edch", "scale": [{"value": 1, "label": "1", "kind": "radio"}, {"value": 2, "label": "2", "kind": "radio"}, {"value": 3, "label": "3", "kind": "radio"}, {"value": 4, "label": "4", "kind": "radio"}, {"value": 5, "label": "5", "kind": "radio"}], "criteria": ["AI t\u1ef1 \u0111\u1ed9ng t\u1ed5ng h\u1ee3p b\u00e1o c\u00e1o", "AI ph\u00e2n t\u00edch xu h\u01b0\u1edbng CCHC", "AI d\u1ef1 b\u00e1o nguy c\u01a1 kh\u00f4ng ho\u00e0n th\u00e0nh nhi\u1ec7m v\u1ee5", "AI g\u1ee3i \u00fd c\u00e1c ti\u00eau ch\u00ed c\u00f2n y\u1ebfu", "AI h\u1ecfi \u0111\u00e1p s\u1ed1 li\u1ec7u CCHC b\u1eb1ng ng\u00f4n ng\u1eef t\u1ef1 nhi\u00ean"]}','2026-07-01 06:14:26.776285','2026-07-01 06:14:26.776303',5,349,'question'),
 (7899,'1. Dashboard quan trọng nhất cần ưu tiên xây dựng','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 06:14:26.856262','2026-07-01 06:14:26.856275',2,350,'question'),
 (7900,'2. Báo cáo quan trọng nhất cần ưu tiên','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 06:14:26.872358','2026-07-01 06:14:26.872371',2,350,'question'),
 (7901,'3. Các KPI cần bổ sung','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 06:14:26.887232','2026-07-01 06:14:26.887245',2,350,'question'),
 (7902,'4. Đề xuất khác','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 06:14:26.901678','2026-07-01 06:14:26.901691',2,350,'question'),
 (7984,'BM-09: Phiếu khảo sát yêu cầu chức năng và phi chức năng hệ thống','',0,0,'[]','{}','{}','2026-07-01 11:38:00.783152','2026-07-01 11:38:00.783165',8,351,'question'),
 (7985,'Thu thập các yêu cầu đối với Hệ thống theo dõi, đánh giá CCHC nhằm:','',0,0,'[]','{}','{}','2026-07-01 11:38:00.797060','2026-07-01 11:38:00.797082',9,351,'question'),
 (7986,'• Xác định đầy đủ các chức năng nghiệp vụ cần xây dựng.
• Xác định mức độ ưu tiên của từng chức năng.
• Thu thập các yêu cầu về hiệu năng, bảo mật, tích hợp và vận hành.
• Làm cơ sở xây dựng BRS, FRD và thiết kế hệ thống.','',0,0,'[]','{}','{}','2026-07-01 11:38:00.811125','2026-07-01 11:38:00.811138',9,351,'question'),
 (7987,'Đơn vị:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 11:38:00.922768','2026-07-01 11:38:00.922784',1,352,'question'),
 (7988,'Người cung cấp:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 11:38:00.938724','2026-07-01 11:38:00.938738',1,352,'question'),
 (7989,'Chức vụ:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 11:38:00.951744','2026-07-01 11:38:00.951757',1,352,'question'),
 (7990,'Bộ phận:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 11:38:00.964828','2026-07-01 11:38:00.964849',1,352,'question'),
 (7991,'Điện thoại:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 11:38:00.978075','2026-07-01 11:38:00.978095',1,352,'question'),
 (7992,'Email:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 11:38:00.991539','2026-07-01 11:38:00.991554',1,352,'question'),
 (7993,'A. YÊU CẦU VỀ CHỨC NĂNG','',0,0,'[]','{}','{}','2026-07-01 11:38:01.213685','2026-07-01 11:38:01.213699',8,353,'question'),
 (7994,'1. Quản lý danh mục','Đánh giá mức độ cần thiết (1 = Không cần; 5 = Rất cần)',1,0,'[]','{}','{"grid_type": "scale5", "criteria_label": "Ch\u1ee9c n\u0103ng", "scale": [{"value": 1, "label": "1", "kind": "radio"}, {"value": 2, "label": "2", "kind": "radio"}, {"value": 3, "label": "3", "kind": "radio"}, {"value": 4, "label": "4", "kind": "radio"}, {"value": 5, "label": "5", "kind": "radio"}], "criteria": ["Qu\u1ea3n l\u00fd danh m\u1ee5c \u0111\u01a1n v\u1ecb", "Qu\u1ea3n l\u00fd ng\u01b0\u1eddi d\u00f9ng", "Qu\u1ea3n l\u00fd ti\u00eau ch\u00ed CCHC", "Qu\u1ea3n l\u00fd lo\u1ea1i minh ch\u1ee9ng", "Qu\u1ea3n l\u00fd k\u1ef3 \u0111\u00e1nh gi\u00e1"]}','2026-07-01 11:38:01.227090','2026-07-01 11:38:01.227104',5,353,'question'),
 (7995,'2. Quản lý kế hoạch và nhiệm vụ','',1,0,'[]','{}','{"grid_type": "scale5", "criteria_label": "Ch\u1ee9c n\u0103ng", "scale": [{"value": 1, "label": "1", "kind": "radio"}, {"value": 2, "label": "2", "kind": "radio"}, {"value": 3, "label": "3", "kind": "radio"}, {"value": 4, "label": "4", "kind": "radio"}, {"value": 5, "label": "5", "kind": "radio"}], "criteria": ["L\u1eadp k\u1ebf ho\u1ea1ch CCHC", "Giao nhi\u1ec7m v\u1ee5", "Theo d\u00f5i ti\u1ebfn \u0111\u1ed9", "Nh\u1eafc vi\u1ec7c t\u1ef1 \u0111\u1ed9ng", "C\u1ea3nh b\u00e1o qu\u00e1 h\u1ea1n"]}','2026-07-01 11:38:01.241479','2026-07-01 11:38:01.241492',5,353,'question'),
 (7996,'3. Quản lý hồ sơ minh chứng','',1,0,'[]','{}','{"grid_type": "scale5", "criteria_label": "Ch\u1ee9c n\u0103ng", "scale": [{"value": 1, "label": "1", "kind": "radio"}, {"value": 2, "label": "2", "kind": "radio"}, {"value": 3, "label": "3", "kind": "radio"}, {"value": 4, "label": "4", "kind": "radio"}, {"value": 5, "label": "5", "kind": "radio"}], "criteria": ["Upload h\u1ed3 s\u01a1 minh ch\u1ee9ng", "Qu\u1ea3n l\u00fd phi\u00ean b\u1ea3n t\u00e0i li\u1ec7u", "K\u00fd s\u1ed1 h\u1ed3 s\u01a1", "T\u00ecm ki\u1ebfm minh ch\u1ee9ng", "Ph\u00e2n lo\u1ea1i minh ch\u1ee9ng"]}','2026-07-01 11:38:01.255042','2026-07-01 11:38:01.255056',5,353,'question'),
 (7997,'4. Đánh giá và chấm điểm','',1,0,'[]','{}','{"grid_type": "scale5", "criteria_label": "Ch\u1ee9c n\u0103ng", "scale": [{"value": 1, "label": "1", "kind": "radio"}, {"value": 2, "label": "2", "kind": "radio"}, {"value": 3, "label": "3", "kind": "radio"}, {"value": 4, "label": "4", "kind": "radio"}, {"value": 5, "label": "5", "kind": "radio"}], "criteria": ["T\u1ef1 \u0111\u00e1nh gi\u00e1", "Ch\u1ea5m \u0111i\u1ec3m t\u1ef1 \u0111\u1ed9ng", "Th\u1ea9m \u0111\u1ecbnh", "Ph\u00ea duy\u1ec7t k\u1ebft qu\u1ea3", "L\u01b0u l\u1ecbch s\u1eed ch\u1ea5m \u0111i\u1ec3m"]}','2026-07-01 11:38:01.268865','2026-07-01 11:38:01.268884',5,353,'question'),
 (7998,'5. Báo cáo và Dashboard','',1,0,'[]','{}','{"grid_type": "scale5", "criteria_label": "Ch\u1ee9c n\u0103ng", "scale": [{"value": 1, "label": "1", "kind": "radio"}, {"value": 2, "label": "2", "kind": "radio"}, {"value": 3, "label": "3", "kind": "radio"}, {"value": 4, "label": "4", "kind": "radio"}, {"value": 5, "label": "5", "kind": "radio"}], "criteria": ["Dashboard \u0111i\u1ec1u h\u00e0nh", "Dashboard KPI", "Dashboard ti\u1ebfn \u0111\u1ed9", "B\u00e1o c\u00e1o \u0111\u1ed9ng", "Xu\u1ea5t Excel/PDF/Word"]}','2026-07-01 11:38:01.282301','2026-07-01 11:38:01.282317',5,353,'question'),
 (7999,'6. Quản trị hệ thống','',1,0,'[]','{}','{"grid_type": "scale5", "criteria_label": "Ch\u1ee9c n\u0103ng", "scale": [{"value": 1, "label": "1", "kind": "radio"}, {"value": 2, "label": "2", "kind": "radio"}, {"value": 3, "label": "3", "kind": "radio"}, {"value": 4, "label": "4", "kind": "radio"}, {"value": 5, "label": "5", "kind": "radio"}], "criteria": ["Qu\u1ea3n l\u00fd ng\u01b0\u1eddi d\u00f9ng", "Qu\u1ea3n l\u00fd vai tr\u00f2", "Ph\u00e2n quy\u1ec1n", "Nh\u1eadt k\u00fd h\u1ec7 th\u1ed1ng"]}','2026-07-01 11:38:01.295926','2026-07-01 11:38:01.295938',5,353,'question'),
 (8000,'7. AI và tự động hóa','',1,0,'[]','{}','{"grid_type": "scale5", "criteria_label": "Ch\u1ee9c n\u0103ng", "scale": [{"value": 1, "label": "1", "kind": "radio"}, {"value": 2, "label": "2", "kind": "radio"}, {"value": 3, "label": "3", "kind": "radio"}, {"value": 4, "label": "4", "kind": "radio"}, {"value": 5, "label": "5", "kind": "radio"}], "criteria": ["AI t\u1ed5ng h\u1ee3p b\u00e1o c\u00e1o", "AI ph\u00e2n t\u00edch k\u1ebft qu\u1ea3 CCHC", "AI ph\u00e1t hi\u1ec7n nguy c\u01a1 ch\u1eadm ti\u1ebfn \u0111\u1ed9", "AI g\u1ee3i \u00fd c\u1ea3i thi\u1ec7n ch\u1ec9 s\u1ed1 CCHC", "AI Chatbot h\u1ed7 tr\u1ee3 nghi\u1ec7p v\u1ee5"]}','2026-07-01 11:38:01.309116','2026-07-01 11:38:01.309128',5,353,'question'),
 (8001,'8. Mức độ ưu tiên','Đánh dấu mức ưu tiên của từng nhóm chức năng',1,0,'[]','{}','{"grid_type": "yesno", "criteria_label": "Nh\u00f3m ch\u1ee9c n\u0103ng", "scale": [{"value": 1, "label": "\u01afu ti\u00ean cao", "kind": "radio"}, {"value": 2, "label": "Trung b\u00ecnh", "kind": "radio"}, {"value": 3, "label": "Th\u1ea5p", "kind": "radio"}], "criteria": ["Qu\u1ea3n l\u00fd k\u1ebf ho\u1ea1ch", "Qu\u1ea3n l\u00fd nhi\u1ec7m v\u1ee5", "H\u1ed3 s\u01a1 minh ch\u1ee9ng", "Ch\u1ea5m \u0111i\u1ec3m", "Dashboard", "B\u00e1o c\u00e1o", "AI"]}','2026-07-01 11:38:01.322886','2026-07-01 11:38:01.322898',5,353,'question'),
 (8002,'B. KHẢO SÁT YÊU CẦU PHI CHỨC NĂNG','',0,0,'[]','{}','{}','2026-07-01 11:38:01.336748','2026-07-01 11:38:01.336761',8,353,'question'),
 (8003,'1. Hiệu năng','Đánh giá mức độ quan trọng',1,0,'[]','{}','{"grid_type": "yesno", "criteria_label": "Ti\u00eau ch\u00ed", "scale": [{"value": 1, "label": "Th\u1ea5p", "kind": "radio"}, {"value": 2, "label": "TB", "kind": "radio"}, {"value": 3, "label": "Cao", "kind": "radio"}], "criteria": ["T\u1ed1c \u0111\u1ed9 ph\u1ea3n h\u1ed3i d\u01b0\u1edbi 3 gi\u00e2y", "H\u1ed7 tr\u1ee3 nhi\u1ec1u ng\u01b0\u1eddi d\u00f9ng \u0111\u1ed3ng th\u1eddi", "Kh\u1ea3 n\u0103ng m\u1edf r\u1ed9ng"]}','2026-07-01 11:38:01.350368','2026-07-01 11:38:01.350380',5,353,'question'),
 (8004,'2. Bảo mật','',1,0,'[]','{}','{"grid_type": "checklist", "criteria_label": "N\u1ed9i dung", "scale": [{"value": 1, "label": "C\u1ea7n", "kind": "checkbox"}], "criteria": ["\u0110\u0103ng nh\u1eadp m\u1ed9t l\u1ea7n (SSO)", "MFA", "M\u00e3 h\u00f3a d\u1eef li\u1ec7u", "Nh\u1eadt k\u00fd Audit Log", "Ph\u00e2n quy\u1ec1n chi ti\u1ebft", "Ch\u1eef k\u00fd s\u1ed1"]}','2026-07-01 11:38:01.365038','2026-07-01 11:38:01.365052',5,353,'question'),
 (8005,'3. Tính sẵn sàng','',1,0,'[]','{}','{"grid_type": "checklist", "criteria_label": "N\u1ed9i dung", "scale": [{"value": 1, "label": "C\u1ea7n", "kind": "checkbox"}], "criteria": ["Backup t\u1ef1 \u0111\u1ed9ng", "Kh\u00f4i ph\u1ee5c d\u1eef li\u1ec7u", "High Availability", "Gi\u00e1m s\u00e1t h\u1ec7 th\u1ed1ng"]}','2026-07-01 11:38:01.380835','2026-07-01 11:38:01.380849',5,353,'question'),
 (8006,'4. Khả năng tích hợp','Đơn vị có nhu cầu tích hợp với hệ thống nào?',1,0,'[]','{}','{"grid_type": "checklist", "criteria_label": "H\u1ec7 th\u1ed1ng", "scale": [{"value": 1, "label": "C\u00f3", "kind": "checkbox"}], "criteria": ["LGSP Th\u00e0nh ph\u1ed1", "H\u1ec7 th\u1ed1ng Qu\u1ea3n l\u00fd v\u0103n b\u1ea3n", "H\u1ec7 th\u1ed1ng M\u1ed9t c\u1eeda", "Kho d\u1eef li\u1ec7u d\u00f9ng chung", "SSO", "H\u1ec7 th\u1ed1ng th\u01b0 \u0111i\u1ec7n t\u1eed", "SMS Gateway"]}','2026-07-01 11:38:01.393557','2026-07-01 11:38:01.393570',5,353,'question'),
 (8007,'5. Khả năng sử dụng','',1,0,'[]','{}','{"grid_type": "checklist", "criteria_label": "Ti\u00eau ch\u00ed", "scale": [{"value": 1, "label": "C\u00f3", "kind": "checkbox"}], "criteria": ["Giao di\u1ec7n th\u00e2n thi\u1ec7n", "Responsive tr\u00ean Mobile", "H\u1ed7 tr\u1ee3 \u0111a tr\u00ecnh duy\u1ec7t", "H\u1ed7 tr\u1ee3 \u0111a ng\u00f4n ng\u1eef", "H\u1ed7 tr\u1ee3 ng\u01b0\u1eddi khuy\u1ebft t\u1eadt"]}','2026-07-01 11:38:01.407180','2026-07-01 11:38:01.407197',5,353,'question'),
 (8008,'1. Theo đơn vị, ba chức năng quan trọng nhất cần xây dựng','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 11:38:01.476867','2026-07-01 11:38:01.476881',2,354,'question'),
 (8009,'2. Ba yêu cầu kỹ thuật quan trọng nhất','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 11:38:01.489892','2026-07-01 11:38:01.489904',2,354,'question'),
 (8010,'3. Các đề xuất khác','',0,0,'[]','{}','{"placeholder": ""}','2026-07-01 11:38:01.502915','2026-07-01 11:38:01.502928',2,354,'question'),
 (8089,'BM-03: Phiếu khảo sát lãnh đạo quản lý CCHC','',0,0,'[]','{}','{}','2026-07-04 17:18:32.168174','2026-07-04 17:18:32.168174',8,311,'question'),
 (8090,'Thu thập ý kiến của lãnh đạo các cấp về:','',0,0,'[]','{}','{}','2026-07-04 17:18:32.190152','2026-07-04 17:18:32.190152',9,311,'question'),
 (8091,'• Hiện trạng công tác quản lý, chỉ đạo điều hành CCHC.
• Các khó khăn, hạn chế trong công tác theo dõi, đánh giá CCHC.
• Các nhu cầu quản lý, điều hành và khai thác thông tin.
• Các yêu cầu đối với Hệ thống theo dõi, đánh giá CCHC các cấp thành phố Hà Nội.','',0,0,'[]','{}','{}','2026-07-04 17:18:32.220990','2026-07-04 17:18:32.220990',9,311,'question'),
 (8092,'Đơn vị:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-04 17:18:32.483839','2026-07-04 17:18:32.483839',1,312,'question'),
 (8093,'Người cung cấp:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-04 17:18:32.513318','2026-07-04 17:18:32.513318',1,312,'question'),
 (8094,'Chức vụ:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-04 17:18:32.545645','2026-07-04 17:18:32.545645',1,312,'question'),
 (8095,'Bộ phận:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-04 17:18:32.577568','2026-07-04 17:18:32.577568',1,312,'question'),
 (8096,'Điện thoại:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-04 17:18:32.607923','2026-07-04 17:18:32.607923',1,312,'question'),
 (8097,'Email:','',0,0,'[]','{}','{"placeholder": ""}','2026-07-04 17:18:32.632922','2026-07-04 17:18:32.634205',1,312,'question'),
 (8098,'A. Đánh giá chung','',0,0,'[]','{}','{}','2026-07-04 17:18:33.170274','2026-07-04 17:18:33.170274',8,313,'question'),
 (8099,'1. Ông/ Bà đánh giá mức độ hiệu quả của công tác theo dõi, đánh giá CCHC hiện nay tại đơn vị?','(Chọn 1 phương án)',1,0,'["R\u1ea5t t\u1ed1t", "T\u1ed1t", "Trung b\u00ecnh", "Ch\u01b0a t\u1ed1t", "K\u00e9m"]','{}','{"options": ["R\u1ea5t t\u1ed1t", "T\u1ed1t", "Trung b\u00ecnh", "Ch\u01b0a t\u1ed1t", "K\u00e9m"]}','2026-07-04 17:18:33.211682','2026-07-04 17:18:33.211682',4,313,'question'),
 (8100,'2. Theo Ông/Bà, những khó khăn lớn nhất trong công tác quản lý, theo dõi và đánh giá CCHC hiện nay là gì?','(Có thể chọn nhiều phương án)',1,0,'["Kh\u00f3 theo d\u00f5i ti\u1ebfn \u0111\u1ed9 th\u1ef1c hi\u1ec7n nhi\u1ec7m v\u1ee5", "D\u1eef li\u1ec7u ph\u00e2n t\u00e1n t\u1ea1i nhi\u1ec1u \u0111\u01a1n v\u1ecb", "Thi\u1ebfu c\u00f4ng c\u1ee5 t\u1ed5ng h\u1ee3p b\u00e1o c\u00e1o", "Kh\u00f3 qu\u1ea3n l\u00fd h\u1ed3 s\u01a1 minh ch\u1ee9ng", "Kh\u00f3 \u0111\u00e1nh gi\u00e1, so s\u00e1nh k\u1ebft qu\u1ea3 gi\u1eefa c\u00e1c \u0111\u01a1n v\u1ecb", "Vi\u1ec7c t\u00ednh \u0111i\u1ec3m c\u00f2n th\u1ee7 c\u00f4ng", "Thi\u1ebfu c\u00f4ng c\u1ee5 c\u1ea3nh b\u00e1o, nh\u1eafc vi\u1ec7c", "Thi\u1ebfu dashboard ph\u1ee5c v\u1ee5 \u0111i\u1ec1u h\u00e0nh", "D\u1eef li\u1ec7u ch\u01b0a k\u1ecbp th\u1eddi, thi\u1ebfu ch\u00ednh x\u00e1c", "Kh\u00e1c (ghi r\u00f5): __________________"]','{}','{"options": ["Kh\u00f3 theo d\u00f5i ti\u1ebfn \u0111\u1ed9 th\u1ef1c hi\u1ec7n nhi\u1ec7m v\u1ee5", "D\u1eef li\u1ec7u ph\u00e2n t\u00e1n t\u1ea1i nhi\u1ec1u \u0111\u01a1n v\u1ecb", "Thi\u1ebfu c\u00f4ng c\u1ee5 t\u1ed5ng h\u1ee3p b\u00e1o c\u00e1o", "Kh\u00f3 qu\u1ea3n l\u00fd h\u1ed3 s\u01a1 minh ch\u1ee9ng", "Kh\u00f3 \u0111\u00e1nh gi\u00e1, so s\u00e1nh k\u1ebft qu\u1ea3 gi\u1eefa c\u00e1c \u0111\u01a1n v\u1ecb", "Vi\u1ec7c t\u00ednh \u0111i\u1ec3m c\u00f2n th\u1ee7 c\u00f4ng", "Thi\u1ebfu c\u00f4ng c\u1ee5 c\u1ea3nh b\u00e1o, nh\u1eafc vi\u1ec7c", "Thi\u1ebfu dashboard ph\u1ee5c v\u1ee5 \u0111i\u1ec1u h\u00e0nh", "D\u1eef li\u1ec7u ch\u01b0a k\u1ecbp th\u1eddi, thi\u1ebfu ch\u00ednh x\u00e1c", "Kh\u00e1c (ghi r\u00f5): __________________"]}','2026-07-04 17:18:33.252371','2026-07-04 17:18:33.253369',4,313,'question'),
 (8101,'3. Ông/Bà đánh giá mức độ ảnh hưởng của các khó khăn trên?','(Chọn 1 phương án)',1,0,'["R\u1ea5t cao", "Cao", "Trung b\u00ecnh", "Th\u1ea5p"]','{}','{"options": ["R\u1ea5t cao", "Cao", "Trung b\u00ecnh", "Th\u1ea5p"]}','2026-07-04 17:18:33.286365','2026-07-04 17:18:33.286365',4,313,'question'),
 (8102,'B. Nhu cầu thông tin phục vụ chỉ đạo điều hành','',0,0,'[]','{}','{}','2026-07-04 17:18:33.336739','2026-07-04 17:18:33.336739',8,313,'question'),
 (8103,'1. Các chỉ số lãnh đạo cần theo dõi','(Vui lòng đánh giá mức độ cần thiết của các chỉ số sau: 1: Không cần; 5: Rất cần)',1,0,'[]','{}','{"grid_type": "scale5", "criteria_label": "Ch\u1ec9 s\u1ed1", "scale": [{"value": 1, "label": "1", "kind": "radio"}, {"value": 2, "label": "2", "kind": "radio"}, {"value": 3, "label": "3", "kind": "radio"}, {"value": 4, "label": "4", "kind": "radio"}, {"value": 5, "label": "5", "kind": "radio"}], "criteria": ["T\u1ef7 l\u1ec7 ho\u00e0n th\u00e0nh nhi\u1ec7m v\u1ee5 CCHC", "S\u1ed1 nhi\u1ec7m v\u1ee5 qu\u00e1 h\u1ea1n", "Ti\u1ebfn \u0111\u1ed9 th\u1ef1c hi\u1ec7n k\u1ebf ho\u1ea1ch CCHC", "K\u1ebft qu\u1ea3 ch\u1ea5m \u0111i\u1ec3m CCHC", "X\u1ebfp h\u1ea1ng CCHC c\u00e1c \u0111\u01a1n v\u1ecb", "T\u00ecnh tr\u1ea1ng n\u1ed9p h\u1ed3 s\u01a1 minh ch\u1ee9ng", "T\u1ef7 l\u1ec7 ti\u00eau ch\u00ed ho\u00e0n th\u00e0nh", "So s\u00e1nh k\u1ebft qu\u1ea3 gi\u1eefa c\u00e1c n\u0103m", "Ph\u00e2n t\u00edch xu h\u01b0\u1edbng c\u1ea3i thi\u1ec7n CCHC", "C\u00e1c ch\u1ec9 s\u1ed1 kh\u00e1c", "...."]}','2026-07-04 17:18:33.373714','2026-07-04 17:18:33.373714',5,313,'question'),
 (8104,'2. Nhu cầu Dashboard điều hành','Ông/Bà mong muốn hệ thống cung cấp những Dashboard nào?',1,0,'[]','{}','{"grid_type": "yesno", "criteria_label": "Dashboard", "scale": [{"value": 1, "label": "C\u1ea7n", "kind": "radio"}, {"value": 2, "label": "Kh\u00f4ng c\u1ea7n", "kind": "radio"}], "criteria": ["Dashboard t\u1ed5ng th\u1ec3 CCHC to\u00e0n Th\u00e0nh ph\u1ed1", "Dashboard theo S\u1edf, ng\u00e0nh", "Dashboard theo x\u00e3, ph\u01b0\u1eddng", "Dashboard ti\u1ebfn \u0111\u1ed9 nhi\u1ec7m v\u1ee5", "Dashboard h\u1ed3 s\u01a1 minh ch\u1ee9ng", "Dashboard ch\u1ea5m \u0111i\u1ec3m v\u00e0 x\u1ebfp h\u1ea1ng", "Dashboard c\u1ea3nh b\u00e1o r\u1ee7i ro"]}','2026-07-04 17:18:33.402952','2026-07-04 17:18:33.402952',5,313,'question'),
 (8105,'C. Khảo sát hiện trạng phần mềm đang sử dụng','',0,0,'[]','{}','{}','2026-07-04 17:18:33.451542','2026-07-04 17:18:33.451542',8,313,'question'),
 (8106,'1. Các phần mềm phục vụ công tác CCHC','',1,0,'[]','{}','{"grid_type": "yesno", "criteria_label": "STT", "scale": [{"value": 1, "label": "T\u00ean ph\u1ea7n m\u1ec1m", "kind": "radio"}, {"value": 2, "label": "\u0110\u01a1n v\u1ecb cung c\u1ea5p", "kind": "radio"}, {"value": 3, "label": "H\u00ecnh th\u1ee9c", "kind": "radio"}], "criteria": ["1", "2", "3"]}','2026-07-04 17:18:33.489377','2026-07-04 17:18:33.489377',5,313,'question'),
 (8107,'2. Đánh giá mức độ đáp ứng','',1,0,'[]','{}','{"grid_type": "yesno", "criteria_label": "Ti\u00eau ch\u00ed", "scale": [{"value": 1, "label": "R\u1ea5t t\u1ed1t", "kind": "radio"}, {"value": 2, "label": "T\u1ed1t", "kind": "radio"}, {"value": 3, "label": "Trung b\u00ecnh", "kind": "radio"}, {"value": 4, "label": "K\u00e9m", "kind": "radio"}], "criteria": ["Qu\u1ea3n l\u00fd k\u1ebf ho\u1ea1ch CCHC", "Qu\u1ea3n l\u00fd nhi\u1ec7m v\u1ee5", "Qu\u1ea3n l\u00fd minh ch\u1ee9ng", "B\u00e1o c\u00e1o th\u1ed1ng k\u00ea", "Dashboard \u0111i\u1ec1u h\u00e0nh", "T\u00edch h\u1ee3p d\u1eef li\u1ec7u"]}','2026-07-04 17:18:33.527120','2026-07-04 17:18:33.527120',5,313,'question'),
 (8108,'3. Những hạn chế của phần mềm hiện tại','',1,0,'["Giao di\u1ec7n kh\u00f3 s\u1eed d\u1ee5ng", "T\u1ed1c \u0111\u1ed9 x\u1eed l\u00fd ch\u1eadm", "Thi\u1ebfu b\u00e1o c\u00e1o", "Thi\u1ebfu Dashboard", "Kh\u00f4ng h\u1ed7 tr\u1ee3 thi\u1ebft b\u1ecb di \u0111\u1ed9ng", "Thi\u1ebfu ch\u1ee9c n\u0103ng c\u1ea3nh b\u00e1o", "Kh\u00f3 qu\u1ea3n l\u00fd h\u1ed3 s\u01a1 minh ch\u1ee9ng", "Kh\u00f3 t\u00edch h\u1ee3p d\u1eef li\u1ec7u", "Kh\u00e1c: __________________"]','{}','{"options": ["Giao di\u1ec7n kh\u00f3 s\u1eed d\u1ee5ng", "T\u1ed1c \u0111\u1ed9 x\u1eed l\u00fd ch\u1eadm", "Thi\u1ebfu b\u00e1o c\u00e1o", "Thi\u1ebfu Dashboard", "Kh\u00f4ng h\u1ed7 tr\u1ee3 thi\u1ebft b\u1ecb di \u0111\u1ed9ng", "Thi\u1ebfu ch\u1ee9c n\u0103ng c\u1ea3nh b\u00e1o", "Kh\u00f3 qu\u1ea3n l\u00fd h\u1ed3 s\u01a1 minh ch\u1ee9ng", "Kh\u00f3 t\u00edch h\u1ee3p d\u1eef li\u1ec7u", "Kh\u00e1c: __________________"]}','2026-07-04 17:18:33.561488','2026-07-04 17:18:33.561488',4,313,'question'),
 (8109,'D. Nhu cầu đối với hệ thống mới','',0,0,'[]','{}','{}','2026-07-04 17:18:33.593395','2026-07-04 17:18:33.593395',8,313,'question'),
 (8110,'1. Đánh giá mức độ cần thiết của các chức năng','(1: Không cần; 5: Rất cần)',1,0,'[]','{}','{"grid_type": "scale5", "criteria_label": "Ch\u1ee9c n\u0103ng", "scale": [{"value": 1, "label": "1", "kind": "radio"}, {"value": 2, "label": "2", "kind": "radio"}, {"value": 3, "label": "3", "kind": "radio"}, {"value": 4, "label": "4", "kind": "radio"}, {"value": 5, "label": "5", "kind": "radio"}], "criteria": ["Qu\u1ea3n l\u00fd k\u1ebf ho\u1ea1ch CCHC", "Qu\u1ea3n l\u00fd nhi\u1ec7m v\u1ee5", "Qu\u1ea3n l\u00fd h\u1ed3 s\u01a1 minh ch\u1ee9ng", "T\u1ef1 \u0111\u1ed9ng t\u00ednh \u0111i\u1ec3m CCHC", "Dashboard \u0111i\u1ec1u h\u00e0nh", "B\u00e1o c\u00e1o t\u1ef1 \u0111\u1ed9ng", "C\u1ea3nh b\u00e1o qu\u00e1 h\u1ea1n", "Qu\u1ea3n l\u00fd tr\u00ean thi\u1ebft b\u1ecb di \u0111\u1ed9ng", "T\u00edch h\u1ee3p d\u1eef li\u1ec7u d\u00f9ng chung", "AI h\u1ed7 tr\u1ee3 ph\u00e2n t\u00edch d\u1eef li\u1ec7u", "...."]}','2026-07-04 17:18:33.631973','2026-07-04 17:18:33.631973',5,313,'question'),
 (8111,'2. Nhu cầu tiện ích nâng cao','',1,0,'[]','{}','{"grid_type": "yesno", "criteria_label": "Ti\u1ec7n \u00edch", "scale": [{"value": 1, "label": "C\u00f3 nhu c\u1ea7u", "kind": "radio"}, {"value": 2, "label": "Kh\u00f4ng", "kind": "radio"}], "criteria": ["G\u1eedi Email nh\u1eafc vi\u1ec7c", "G\u1eedi th\u00f4ng b\u00e1o tr\u00ean App", "Dashboard tr\u00ean \u0111i\u1ec7n tho\u1ea1i", "K\u00fd s\u1ed1 h\u1ed3 s\u01a1 minh ch\u1ee9ng", "Tr\u1ee3 l\u00fd AI h\u1ed7 tr\u1ee3 khai th\u00e1c d\u1eef li\u1ec7u", "Chatbot h\u1ed7 tr\u1ee3 s\u1eed d\u1ee5ng h\u1ec7 th\u1ed1ng", "T\u00ecm ki\u1ebfm th\u00f4ng minh h\u1ed3 s\u01a1 minh ch\u1ee9ng"]}','2026-07-04 17:18:33.667270','2026-07-04 17:18:33.667270',5,313,'question'),
 (8112,'1. Theo Ông/Bà, các chức năng quan trọng nhất hệ thống cần có là gì?','',0,0,'[]','{}','{"placeholder": ""}','2026-07-04 17:18:33.874165','2026-07-04 17:18:33.874165',2,314,'question'),
 (8113,'2. Các yêu cầu đặc thù đối với công tác chỉ đạo, điều hành CCHC','',0,0,'[]','{}','{"placeholder": ""}','2026-07-04 17:18:33.917404','2026-07-04 17:18:33.917404',2,314,'question'),
 (8114,'3. Các kiến nghị khác','',0,0,'[]','{}','{"placeholder": ""}','2026-07-04 17:18:33.967903','2026-07-04 17:18:33.967903',2,314,'question');
INSERT INTO "survey_questiontype" ("id","name","code","icon","has_options","has_validation","created_at") VALUES (1,'Văn bản ngắn','short-text','minus',0,0,'2026-06-25 13:17:47.138346'),
 (2,'Văn bản dài','long-text','text',0,0,'2026-06-25 13:17:47.144602'),
 (3,'Một lựa chọn','single-choice','circle-dot',1,0,'2026-06-25 13:17:47.149850'),
 (4,'Nhiều lựa chọn','multi-choice','check-square',1,0,'2026-06-25 13:17:47.154781'),
 (5,'Lưới đánh giá','rating-grid','grid-3x3',1,0,'2026-06-25 13:17:47.159743'),
 (6,'Bảng dữ liệu','data-table','table',0,0,'2026-06-25 13:17:47.164841'),
 (7,'Thông tin cá nhân','personal-info','user',0,0,'2026-06-25 13:17:47.171494'),
 (8,'Tiêu đề','title','type',0,0,'2026-06-26 02:39:24.905404'),
 (9,'Đoạn văn','paragraph','align-left',0,0,'2026-06-26 02:39:24.907306'),
 (10,'Phần mới','section-break','layout',0,0,'2026-06-26 02:39:24.908969');
INSERT INTO "survey_response" ("id","respondent_ip","respondent_device_id","respondent_email","user_agent","started_at","time_taken","answers","is_verified","verification_token","is_cleaned","is_duplicate","created_at","user_id","survey_id","section_progress","status","submitted_at") VALUES (14,'127.0.0.1',NULL,'hsa@gmail.com','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0','2026-06-30 11:24:12.991708',517,'{"5244": "1", "5280": ["R\u1ea5t cao", "Cao"], "_participant_info": {"agency": "S\u1edf N\u1ed9i v\u1ee5 TP. H\u00e0 N\u1ed9i", "target_group_code": "GRP001", "target_group_name": "Nh\u00f3m \u0111\u1ed1i t\u01b0\u1ee3ng 1", "full_name": "Huy Ho\u00e0ng", "position": "Nv", "department": "Nv", "phone": "09232123212", "email": "hsa@gmail.com", "notes": "", "assigned_forms": ["BM-03"]}, "5414": "\u0110\u00e0o Huy Ho\u00e0ng", "5415": "NV", "5416": "NV", "5417": "098222222222", "5418": "hoang@gmail.com", "5419": "ch\u1ecbu", "5423": ["R\u1ea5t t\u1ed1t"], "5425": ["Kh\u00f3 theo d\u00f5i ti\u1ebfn \u0111\u1ed9 th\u1ef1c hi\u1ec7n nhi\u1ec7m v\u1ee5"], "5427": ["Trung b\u00ecnh"], "5429": "1", "5430": "1", "5432": "1", "5433": "1", "5434": ["T\u1ed1c \u0111\u1ed9 x\u1eed l\u00fd ch\u1eadm", "Kh\u00f4ng h\u1ed7 tr\u1ee3 thi\u1ebft b\u1ecb di \u0111\u1ed9ng"], "5436": "1", "5437": "1", "5438": "Ch\u1ecbu", "5439": "Ch\u1ecbu", "5440": "Ch\u1ecbu", "5846": [["", ""]], "6103": ["Kh\u00e1c: __________________"]}',0,NULL,0,0,'2026-06-30 11:24:12.991750',NULL,29,'{"sec_mr0k5t66_yc2et": 0, "sec_mr0k5t66_fobcy": 100, "sec_mr0k5t66_ggv06": 100, "sec_mr0k5t68_lojpm": 100, "sec_mr0qmi7n_qayw0": 0, "sec_mr0qmi7n_qz4p4": 0, "sec_mr0qmi7p_km13x": 0, "sec_mr1glq8l_5h1n6": 0, "sec_mr1glq8l_0c44r": 0, "sec_mr1glq8l_lxk4d": 10, "sec_mr1glq8n_dexnb": 0}','draft','2026-06-30 13:22:01.435609'),
 (15,'127.0.0.1',NULL,NULL,'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0','2026-07-01 02:45:59.152545',59,'{"6498": ["Theo ng\u00e0y", "Theo tu\u1ea7n"], "6501": "1", "6517": "1"}',0,NULL,0,0,'2026-07-01 02:45:59.152592',NULL,31,'{"sec_mr1gzbqs_wjtmn": 0, "sec_mr1gzbqs_bx124": 0, "sec_mr1gzbqs_ks4n3": 0, "sec_mr1gzbqu_zt24s": 0}','draft',NULL),
 (16,'127.0.0.1',NULL,NULL,'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0','2026-07-01 05:05:13.275029',61,'{"7327": {"type": "grid", "data": [[null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null]]}, "7319": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null], [null, null]]}, "7320": {"type": "grid", "data": [[null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null]]}, "7323": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null], [null, null]]}, "7324": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null], [null, null], [null, null], [null, null], [null, null]]}, "7325": {"type": "grid", "data": [[null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null]]}, "7328": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null], [null, null], [null, null], [null, null], [null, null]]}, "7329": {"type": "grid", "data": [[null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null]]}, "7330": {"type": "grid", "data": [[null, null, null], [null, null, null], [null, null, null], [null, null, null]]}, "7332": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null], [null, null], [null, null], [null, null], [null, null], [null, null], [null, null]]}, "7333": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null]]}, "7335": {"type": "grid", "data": [[null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null]]}, "7336": {"type": "grid", "data": [[null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null]]}, "7351": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null], [null, null]]}, "7352": {"type": "grid", "data": [[null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null]]}, "7355": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null], [null, null]]}, "7356": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null], [null, null], [null, null], [null, null], [null, null]]}, "7357": {"type": "grid", "data": [[null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null]]}, "7359": {"type": "grid", "data": [[null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null]]}, "7360": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null], [null, null], [null, null], [null, null], [null, null]]}, "7361": {"type": "grid", "data": [[null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null]]}, "7362": {"type": "grid", "data": [[null, null, null], [null, null, null], [null, null, null], [null, null, null]]}, "7364": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null], [null, null], [null, null], [null, null], [null, null], [null, null], [null, null]]}, "7365": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null]]}, "7367": {"type": "grid", "data": [[null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null]]}, "7368": {"type": "grid", "data": [[null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null]]}}',0,NULL,0,0,'2026-07-01 05:05:13.275103',NULL,32,'{"sec_mr1kcf4h_q1tuo": 0, "sec_mr1kcf4h_he1ce": 0, "sec_mr1kcf4i_vfptn": 0, "sec_mr1kcf4j_w5zxz": 0}','draft',NULL),
 (17,'127.0.0.1',NULL,NULL,'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0','2026-07-01 05:23:38.916390',361,'{"7442": {"type": "grid", "data": [[null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null]]}, "7444": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null], [null, null], [null, null], [null, null], [null, null], [null, null], [null, null]]}, "7445": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null], [null, null]]}, "7446": {"type": "grid", "data": [[null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null]]}, "7449": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null], [null, null], [null, null], [null, null]]}, "7450": {"type": "grid", "data": [[null, null, null], [null, null, null], [null, null, null], [null, null, null]]}, "7452": {"type": "grid", "data": [[null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null]]}, "7453": {"type": "grid", "data": [[null, null, null], [null, null, null], [null, null, null], [null, null, null]]}, "7455": {"type": "grid", "data": [[null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null]]}, "7456": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null], [null, null], [null, null]]}, "7457": {"type": "grid", "data": [[null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null]]}, "7447": ["Kh\u00e1c"], "7532": {"type": "grid", "data": [[null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null]]}, "7534": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null], [null, null], [null, null], [null, null], [null, null], [null, null], [null, null]]}, "7535": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null], [null, null]]}, "7536": {"type": "grid", "data": [[null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null]]}, "7539": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null], [null, null], [null, null], [null, null]]}, "7540": {"type": "grid", "data": [[null, null, null], [null, null, null], [null, null, null], [null, null, null]]}, "7542": {"type": "grid", "data": [[null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null]]}, "7543": {"type": "grid", "data": [[null, null, null], [null, null, null], [null, null, null], [null, null, null]]}, "7545": {"type": "grid", "data": [[null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null]]}, "7546": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null], [null, null], [null, null]]}, "7547": {"type": "grid", "data": [[null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null]]}}',0,NULL,0,0,'2026-07-01 05:23:38.916437',NULL,33,'{"sec_mr1mpeye_xl8ru": 0, "sec_mr1mpeyf_agv21": 0, "sec_mr1mpeyf_gv461": 0, "sec_mr1mpeyg_5bcha": 0}','draft',NULL),
 (18,'127.0.0.1',NULL,NULL,'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0','2026-07-01 05:45:05.998934',460,'{"7749": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null], [null, null]]}, "7751": {"type": "grid", "data": [[null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null]]}, "7755": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null]]}, "7757": {"type": "grid", "data": [[null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null]]}, "7761": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null]]}, "7762": {"type": "grid", "data": [[null, null], [null, null], [null, null]]}, "7765": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null]]}, "7766": {"type": "grid", "data": [[null, null], [null, null], [null, null]]}, "7767": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null]]}, "7768": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null], [null, null], [null, null], [null, null]]}, "7769": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null]]}, "7772": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null]]}}',0,NULL,0,0,'2026-07-01 05:45:05.998978',NULL,34,'{"sec_mr1nfhyy_n59sv": 0, "sec_mr1nfhyy_ho4w8": 0, "sec_mr1nfhyy_fcbug": 0, "sec_mr1nfhz0_ar2rv": 0}','draft',NULL),
 (19,'127.0.0.1',NULL,'hsa@gmail.com','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0','2026-07-01 08:03:33.258885',6,'{"_participant_info": {"agency": "S\u1edf N\u1ed9i v\u1ee5 TP. H\u00e0 N\u1ed9i", "target_group_code": "GRP001", "target_group_name": "Nh\u00f3m \u0111\u1ed1i t\u01b0\u1ee3ng 1", "full_name": "\u0110\u00e0o Huy Ho\u00e0ng", "position": "Nv", "department": "Nv", "phone": "09232123212", "email": "hsa@gmail.com", "notes": "", "assigned_forms": ["BM-09", "BM-08", "BM-03"]}, "7933": "1", "7934": "2", "7935": "3", "7936": "4", "7937": "5", "7938": "6", "7940": {"type": "grid", "data": [[null, "1", null, null, null, null], [null, null, "2", null, null, null], [null, null, null, "3", null, null], [null, null, null, null, "4", null], [null, null, null, null, "4", null]]}, "7941": {"type": "grid", "data": [[null, "1", null, null, null, null], [null, null, "2", null, null, null], [null, null, null, "3", null, null], [null, null, null, "3", null, null], [null, null, null, null, "4", null]]}, "7942": {"type": "grid", "data": [[null, "1", null, null, null, null], [null, "1", null, null, null, null], [null, "1", null, null, null, null], [null, "1", null, null, null, null], [null, "1", null, null, null, null]]}, "7943": {"type": "grid", "data": [[null, "1", null, null, null, null], [null, "1", null, null, null, null], [null, "1", null, null, null, null], [null, "1", null, null, null, null], [null, "1", null, null, null, null]]}, "7944": {"type": "grid", "data": [[null, "1", null, null, null, null], [null, "1", null, null, null, null], [null, "1", null, null, null, null], [null, "1", null, null, null, null], [null, "1", null, null, null, null]]}, "7945": {"type": "grid", "data": [[null, "1", null, null, null, null], [null, "1", null, null, null, null], [null, "1", null, null, null, null], [null, "1", null, null, null, null]]}, "7946": {"type": "grid", "data": [[null, "1", null, null, null, null], [null, "1", null, null, null, null], [null, "1", null, null, null, null], [null, "1", null, null, null, null], [null, "1", null, null, null, null]]}, "7947": {"type": "grid", "data": [[null, "1", null, null], [null, "1", null, null], [null, "1", null, null], [null, "1", null, null], [null, "1", null, null], [null, "1", null, null], [null, "1", null, null]]}, "7949": {"type": "grid", "data": [[null, "1", null, null], [null, "1", null, null], [null, "1", null, null]]}, "7950": {"type": "grid", "data": [[null, ["1"]], [null, ["1"]], [null, ["1"]], [null, ["1"]], [null, ["1"]], [null, ["1"]]]}, "7951": {"type": "grid", "data": [[null, ["1"]], [null, ["1"]], [null, ["1"]], [null, ["1"]]]}, "7952": {"type": "grid", "data": [[null, ["1"]], [null, ["1"]], [null, ["1"]], [null, ["1"]], [null, ["1"]], [null, ["1"]], [null, ["1"]]]}, "7953": {"type": "grid", "data": [[null, ["1"]], [null, ["1"]], [null, ["1"]], [null, ["1"]], [null, ["1"]]]}, "7954": "12", "7955": "123", "7956": "124124"}',0,NULL,0,0,'2026-07-01 08:03:33.258950',NULL,36,'{"sec_mr1omcf1_cg4ga": 0, "sec_mr1omcf1_regwl": 100, "sec_mr1omcf1_1bnfx": 100, "sec_mr1omcf3_r4kid": 100}','submitted','2026-07-01 11:31:14.829328'),
 (20,'127.0.0.1',NULL,NULL,'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0','2026-07-01 09:04:56.326447',0,'{}',0,NULL,0,0,'2026-07-01 09:04:56.326514',NULL,36,'{}','draft',NULL),
 (21,'127.0.0.1',NULL,NULL,'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0','2026-07-01 11:34:47.449369',0,'{}',0,NULL,0,0,'2026-07-01 11:34:47.449419',NULL,29,'{}','draft',NULL),
 (22,'127.0.0.1',NULL,'hoanglc645@gmail.com','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0','2026-07-04 12:33:44.613268',60,'{"_participant_info": {"agency": "H\u00e0 N\u1ed9i", "target_group_code": "GRP001", "target_group_name": "Nh\u00f3m \u0111\u1ed1i t\u01b0\u1ee3ng 1", "full_name": "Accounts1", "position": "1", "department": "2", "phone": "3", "email": "hoanglc645@gmail.com", "notes": "", "assigned_forms": ["BM-09", "BM-08", "BM-03"]}, "7994": {"type": "grid", "data": [[null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null]]}, "7995": {"type": "grid", "data": [[null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null]]}, "7996": {"type": "grid", "data": [[null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null]]}, "7997": {"type": "grid", "data": [[null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null]]}, "7998": {"type": "grid", "data": [[null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null]]}, "7999": {"type": "grid", "data": [[null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null]]}, "8000": {"type": "grid", "data": [[null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null]]}, "8001": {"type": "grid", "data": [[null, null, null, null], [null, null, null, null], [null, null, null, null], [null, null, null, null], [null, null, null, null], [null, null, null, null], [null, null, null, null]]}, "8003": {"type": "grid", "data": [[null, null, null, null], [null, null, null, null], [null, null, null, null]]}, "8004": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null], [null, null], [null, null]]}, "8005": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null]]}, "8006": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null], [null, null], [null, null], [null, null]]}, "8007": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null], [null, null]]}}',0,NULL,0,0,'2026-07-04 12:33:44.613268',NULL,36,'{"sec_mr1omcf1_cg4ga": 0, "sec_mr1omcf1_regwl": 0, "sec_mr1omcf1_1bnfx": 0, "sec_mr1omcf3_r4kid": 0}','draft',NULL),
 (23,'127.0.0.1',NULL,NULL,'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0','2026-07-04 12:46:00.164386',0,'{}',0,NULL,0,0,'2026-07-04 12:46:00.164386',NULL,36,'{}','draft',NULL),
 (24,'127.0.0.1',NULL,NULL,'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0','2026-07-04 17:19:05.862771',120,'{"8103": {"type": "grid", "data": [[null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null]]}, "8104": {"type": "grid", "data": [[null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null]]}, "8106": {"type": "grid", "data": [[null, null, null, null], [null, null, null, null], [null, null, null, null]]}, "8107": {"type": "grid", "data": [[null, null, null, null, null], [null, null, null, null, null], [null, null, null, null, null], [null, null, null, null, null], [null, null, null, null, null], [null, null, null, null, null]]}, "8110": {"type": "grid", "data": [[null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null]]}, "8111": {"type": "grid", "data": [[null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null]]}}',0,NULL,0,0,'2026-07-04 17:19:05.862771',NULL,29,'{"sec_mr1glq8l_5h1n6": 0, "sec_mr1glq8l_0c44r": 0, "sec_mr1glq8l_lxk4d": 0, "sec_mr1glq8n_dexnb": 0}','draft',NULL),
 (25,'127.0.0.1',NULL,NULL,'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0','2026-07-05 06:44:46.245376',5,'{"7987": "Test", "7988": "Test", "7989": "Test", "7990": "Test", "7991": "Test", "7992": "Test", "7994": {"type": "grid", "data": [[null, "1", null, null, null, null], [null, null, "2", null, null, null], [null, null, null, "3", null, null], [null, null, null, null, "4", null], [null, null, null, null, null, "5"]]}, "7995": {"type": "grid", "data": [[null, "1", null, null, null, null], [null, null, "2", null, null, null], [null, null, null, "3", null, null], [null, null, null, null, "4", null], [null, null, null, null, null, "5"]]}, "7996": {"type": "grid", "data": [[null, "1", null, null, null, null], [null, null, "2", null, null, null], [null, null, null, "3", null, null], [null, null, null, null, "4", null], [null, null, null, null, null, "5"]]}, "7997": {"type": "grid", "data": [[null, "1", null, null, null, null], [null, null, "2", null, null, null], [null, null, null, "3", null, null], [null, null, null, null, "4", null], [null, null, null, null, null, "5"]]}, "7998": {"type": "grid", "data": [[null, "1", null, null, null, null], [null, null, "2", null, null, null], [null, null, null, "3", null, null], [null, null, null, null, "4", null], [null, null, null, null, null, "5"]]}, "7999": {"type": "grid", "data": [[null, "1", null, null, null, null], [null, null, null, "3", null, null], [null, null, null, null, "4", null], [null, null, null, null, null, "5"]]}, "8000": {"type": "grid", "data": [[null, "1", null, null, null, null], [null, null, "2", null, null, null], [null, null, null, "3", null, null], [null, null, null, null, "4", null], [null, null, null, null, null, "5"]]}, "8001": {"type": "grid", "data": [[null, "1", null, null], [null, null, "2", null], [null, null, "2", null], [null, null, "2", null], [null, null, "2", null], [null, null, "2", null], [null, null, "2", null]]}, "8003": {"type": "grid", "data": [[null, "1", null, null], [null, null, "2", null], [null, null, "2", null]]}, "8004": {"type": "grid", "data": [[null, ["1"]], [null, ["1"]], [null, ["1"]], [null, ["1"]], [null, ["1"]], [null, ["1"]]]}, "8005": {"type": "grid", "data": [[null, ["1"]], [null, ["1"]], [null, ["1"]], [null, ["1"]]]}, "8006": {"type": "grid", "data": [[null, ["1"]], [null, ["1"]], [null, ["1"]], [null, ["1"]], [null, ["1"]], [null, ["1"]], [null, ["1"]]]}, "8007": {"type": "grid", "data": [[null, ["1"]], [null, ["1"]], [null, ["1"]], [null, ["1"]], [null, ["1"]]]}}',0,NULL,0,0,'2026-07-05 06:44:46.245376',6,36,'{"sec_mr1omcf1_cg4ga": 0, "sec_mr1omcf1_regwl": 100, "sec_mr1omcf1_1bnfx": 100, "sec_mr1omcf3_r4kid": 0}','submitted','2026-07-05 06:46:10.846672'),
 (26,'127.0.0.1',NULL,NULL,'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0','2026-07-05 06:46:28.307852',0,'{}',0,NULL,0,0,'2026-07-05 06:46:28.308852',6,36,'{}','draft',NULL),
 (27,'127.0.0.1',NULL,NULL,'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0','2026-07-05 07:30:01.740905',26,'{"7874": "1", "7876": "`", "7877": "1", "7878": "2", "7879": "3", "7880": "4", "7881": "5", "7882": ["Theo d\u00f5i ti\u1ebfn \u0111\u1ed9 CCHC"], "7883": {"type": "grid", "data": [[null, ["1"]], [null, null], [null, ["1"]], [null, null], [null, null]]}, "7885": {"type": "grid", "data": [[null, null, "2", null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null]]}, "7886": {"type": "grid", "data": [[null, null, null, null, null, null], [null, null, "2", null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null]]}, "7887": {"type": "grid", "data": [[null, null, "2", null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null]]}, "7889": {"type": "grid", "data": [[null, null, null, "3", null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null]]}, "7891": {"type": "grid", "data": [[null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null]]}, "7892": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null], [null, null], [null, null], [null, null]]}, "7893": {"type": "grid", "data": [[null, null], [null, null], [null, null], [null, null], [null, null]]}, "7895": {"type": "grid", "data": [[null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null]]}, "7897": {"type": "grid", "data": [[null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null], [null, null, null]]}, "7898": {"type": "grid", "data": [[null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null]]}}',0,NULL,0,0,'2026-07-05 07:30:01.740905',6,35,'{"sec_mr1ojc0i_3nu1d": 100, "sec_mr1ojc0i_ptznu": 100, "sec_mr1ojc0i_1nk09": 46, "sec_mr1ojc0k_gbed6": 0}','submitted','2026-07-05 07:30:27.757092'),
 (28,'127.0.0.1',NULL,NULL,'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0','2026-07-05 07:30:39.274260',39,'{"8094": "\u01b0", "8103": {"type": "grid", "data": [[null, "1", null, null, null, null], [null, "1", null, null, null, null], [null, null, null, null, null, null], [null, "1", null, null, null, null], [null, "1", null, null, null, null], [null, null, null, null, null, null], [null, "1", null, null, null, null], [null, null, null, null, null, null], [null, "1", null, null, null, null], [null, null, null, null, null, null], [null, null, null, null, null, null]]}, "8104": {"type": "grid", "data": [[null, "1", null], [null, null, "2"], [null, null, "2"], [null, "1", null], [null, "1", null], [null, "1", null], [null, "1", null]]}, "8106": {"type": "grid", "data": [[null, "1", null, null], [null, null, "2", null], [null, null, "2", null]]}, "8107": {"type": "grid", "data": [[null, "1", null, null, null], [null, null, "2", null, null], [null, null, "2", null, null], [null, null, "2", null, null], [null, null, "2", null, null], [null, null, "2", null, null]]}, "8110": {"type": "grid", "data": [[null, "1", null, null, null, null], [null, null, "2", null, null, null], [null, null, null, "3", null, null], [null, null, null, "3", null, null], [null, null, null, "3", null, null], [null, null, null, "3", null, null], [null, null, null, null, "4", null], [null, null, null, null, "4", null], [null, null, null, null, "4", null], [null, null, null, null, "4", null], [null, null, null, null, "4", null]]}, "8111": {"type": "grid", "data": [[null, "1", null], [null, "1", null], [null, null, null], [null, "1", null], [null, null, null], [null, null, null], [null, null, null]]}, "8099": ["Ch\u01b0a t\u1ed1t"], "8100": ["D\u1eef li\u1ec7u ph\u00e2n t\u00e1n t\u1ea1i nhi\u1ec1u \u0111\u01a1n v\u1ecb", "Thi\u1ebfu c\u00f4ng c\u1ee5 c\u1ea3nh b\u00e1o, nh\u1eafc vi\u1ec7c"], "8101": ["R\u1ea5t cao"], "8108": ["Giao di\u1ec7n kh\u00f3 s\u1eed d\u1ee5ng", "T\u1ed1c \u0111\u1ed9 x\u1eed l\u00fd ch\u1eadm"]}',0,NULL,0,0,'2026-07-05 07:30:39.274260',6,29,'{"sec_mr1glq8l_5h1n6": 0, "sec_mr1glq8l_0c44r": 17, "sec_mr1glq8l_lxk4d": 100, "sec_mr1glq8n_dexnb": 0}','submitted','2026-07-05 07:31:18.486503');
INSERT INTO "survey_section" ("id","code","title","description","icon","order","created_at","updated_at","survey_id") VALUES (311,'sec_mr1glq8l_5h1n6','Mục đích','','',0,'2026-07-01 02:31:43.741184','2026-07-04 17:18:32.037183',29),
 (312,'sec_mr1glq8l_0c44r','PHẦN I. THÔNG TIN CHUNG','','',1,'2026-07-01 02:31:43.811654','2026-07-04 17:18:32.245160',29),
 (313,'sec_mr1glq8l_lxk4d','PHẦN II THÔNG TIN CUNG CẤP','','',2,'2026-07-01 02:31:43.909904','2026-07-04 17:18:32.663815',29),
 (314,'sec_mr1glq8n_dexnb','PHẦN III. KIẾN NGHỊ VÀ ĐỀ XUẤT','','',3,'2026-07-01 02:31:44.123599','2026-07-04 17:18:33.687991',29),
 (319,'sec_mr1gzbqs_wjtmn','Mục đích','','',0,'2026-07-01 02:42:05.336983','2026-07-01 02:57:59.239146',31),
 (320,'sec_mr1gzbqs_bx124','PHẦN I. THÔNG TIN CHUNG','','',1,'2026-07-01 02:42:05.386144','2026-07-01 02:57:59.331717',31),
 (321,'sec_mr1gzbqs_ks4n3','PHẦN II THÔNG TIN CUNG CẤP','','',2,'2026-07-01 02:42:05.483132','2026-07-01 02:57:59.519343',31),
 (322,'sec_mr1gzbqu_zt24s','PHẦN III. KIẾN NGHỊ','','',3,'2026-07-01 02:42:05.946367','2026-07-01 02:58:00.395741',31),
 (335,'sec_mr1kcf4h_q1tuo','Mục đích','','',0,'2026-07-01 04:16:19.781773','2026-07-01 05:15:21.074525',32),
 (336,'sec_mr1kcf4h_he1ce','PHẦN I. THÔNG TIN CHUNG','','',1,'2026-07-01 04:16:19.839806','2026-07-01 05:15:21.174411',32),
 (337,'sec_mr1kcf4i_vfptn','PHẦN II. THÔNG TIN CUNG CẤP','','',2,'2026-07-01 04:16:19.928866','2026-07-01 05:15:21.353331',32),
 (338,'sec_mr1kcf4j_w5zxz','PHẦN III. KIẾN NGHỊ','','',3,'2026-07-01 04:16:20.200374','2026-07-01 05:15:21.910970',32),
 (339,'sec_mr1mpeye_xl8ru','Mục đích','','',0,'2026-07-01 05:22:39.616169','2026-07-01 05:25:53.033016',33),
 (340,'sec_mr1mpeyf_agv21','PHẦN I. THÔNG TIN CHUNG','','',1,'2026-07-01 05:22:39.667008','2026-07-01 05:25:53.136781',33),
 (341,'sec_mr1mpeyf_gv461','PHẦN II. THÔNG TIN CUNG CẤP','','',2,'2026-07-01 05:22:39.754754','2026-07-01 05:25:53.336750',33),
 (342,'sec_mr1mpeyg_5bcha','PHẦN III. ĐỀ XUẤT','','',3,'2026-07-01 05:22:39.993799','2026-07-01 05:25:53.812975',33),
 (343,'sec_mr1nfhyy_n59sv','Mục đích','','',0,'2026-07-01 05:42:55.989382','2026-07-01 06:08:53.432445',34),
 (344,'sec_mr1nfhyy_ho4w8','PHẦN I. THÔNG TIN CHUNG','','',1,'2026-07-01 05:42:56.046718','2026-07-01 06:08:53.535322',34),
 (345,'sec_mr1nfhyy_fcbug','PHẦN II','THÔNG TIN CUNG CẤP','',2,'2026-07-01 05:42:56.136713','2026-07-01 06:08:53.697609',34),
 (346,'sec_mr1nfhz0_ar2rv','PHẦN III. ĐỀ XUẤT','','',3,'2026-07-01 05:42:56.478707','2026-07-01 06:08:54.345930',34),
 (347,'sec_mr1ojc0i_3nu1d','Mục đích','','',0,'2026-07-01 06:13:53.133764','2026-07-01 06:14:26.030094',35),
 (348,'sec_mr1ojc0i_ptznu','PHẦN I. THÔNG TIN CHUNG','','',1,'2026-07-01 06:13:53.185142','2026-07-01 06:14:26.147158',35),
 (349,'sec_mr1ojc0i_1nk09','PHẦN II. KHẢO SÁT NHU CẦU KHAI THÁC THÔNG TIN','','',2,'2026-07-01 06:13:53.270985','2026-07-01 06:14:26.314842',35),
 (350,'sec_mr1ojc0k_gbed6','PHẦN III. ĐỀ XUẤT','','',3,'2026-07-01 06:13:53.505306','2026-07-01 06:14:26.788616',35),
 (351,'sec_mr1omcf1_cg4ga','Mục đích','','',0,'2026-07-01 06:16:08.844572','2026-07-01 11:38:00.723820',36),
 (352,'sec_mr1omcf1_regwl','PHẦN I. THÔNG TIN CHUNG','','',1,'2026-07-01 06:16:08.890899','2026-07-01 11:38:00.824098',36),
 (353,'sec_mr1omcf1_1bnfx','PHẦN II. KHẢO SÁT YÊU CẦU CHỨC NĂNG VÀ PHI CHỨC NĂNG CHO HỆ THÔNG MỚI','','',2,'2026-07-01 06:16:08.971350','2026-07-01 11:38:01.003882',36),
 (354,'sec_mr1omcf3_r4kid','PHẦN III. ĐỀ XUẤT','','',3,'2026-07-01 06:16:09.174155','2026-07-01 11:38:01.418703',36);
INSERT INTO "survey_survey" ("id","title","slug","description","start_date","end_date","allow_after_deadline","status","target_groups","settings","created_at","updated_at","category_id","code") VALUES (29,'Phiếu khảo sát lãnh đạo quản lý CCHC','phieu-khao-sat-lanh-ao-quan-ly-cchc','','2026-06-30 11:22:29.281248','2026-07-30 11:22:29.281251',0,'active','[]','{}','2026-06-30 11:22:29.282058','2026-07-04 17:18:31.828946',NULL,'BM-03'),
 (31,'Phiếu khảo sát cán bộ chuyên trách CCHC','phieu-khao-sat-can-bo-chuyen-trach-cchc','','2026-07-01 02:40:00','2026-07-31 02:40:00',0,'active','[]','{}','2026-07-01 02:40:26.762044','2026-07-01 02:57:59.148240',NULL,'BM-04'),
 (32,'Phiếu khảo sát hiện trạng ứng dụng CNTT','phieu-khao-sat-hien-trang-ung-dung-cntt','','2026-07-01 03:02:42.033974','2026-07-31 03:02:42.033978',0,'active','[]','{}','2026-07-01 03:02:42.034843','2026-07-01 05:15:20.976575',NULL,'BM-05'),
 (33,'Phiếu khảo sát hiện trạng dữ liệu','phieu-khao-sat-hien-trang-du-lieu','','2026-07-01 05:21:58.491520','2026-07-31 05:21:58.491523',0,'active','[]','{}','2026-07-01 05:21:58.492306','2026-07-01 05:25:52.967365',NULL,'BM-06'),
 (34,'Phiếu khảo sát hạ tầng kỹ thuật và An toàn thông tin','phieu-khao-sat-ha-tang-ky-thuat-va-an-toan-thong-tin','','2026-07-01 05:42:18.467763','2026-07-31 05:42:18.467765',0,'active','[]','{}','2026-07-01 05:42:18.468318','2026-07-01 06:08:53.366560',NULL,'BM-07'),
 (35,'Phiếu khảo sát nhu cầu Dashboard và báo cáo','phieu-khao-sat-nhu-cau-dashboard-va-bao-cao','','2026-07-01 06:13:16.837275','2026-07-31 06:13:16.837278',0,'active','[]','{}','2026-07-01 06:13:16.838360','2026-07-01 06:14:25.960160',NULL,'BM-08'),
 (36,'Phiếu khảo sát yêu cầu chức năng và phi chức năng hệ thống','phieu-khao-sat-yeu-cau-chuc-nang-va-phi-chuc-nang-he-thong','','2026-07-01 06:15:38.814872','2026-07-31 06:15:38.814874',0,'active','[]','{}','2026-07-01 06:15:38.815691','2026-07-01 11:38:00.654410',NULL,'BM-09');
INSERT INTO "survey_surveyparticipant" ("id","agency","target_group_code","target_group_name","full_name","position","department","phone","email","notes","assigned_forms","ip_address","user_agent","session_key","status","submitted_at","created_at","updated_at","response_id","survey_id","user_id") VALUES (1,'Sở Nội vụ TP. Hà Nội','GRP001','Nhóm đối tượng 1','Huy Hoàng','Nv','Nv','09232123212','hsa@gmail.com','','["BM-03"]','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0','34typck5duw0rogsgbm93b31w56wy62k','draft',NULL,'2026-06-30 13:18:54.455544','2026-07-01 02:34:57.872509',NULL,29,NULL),
 (2,'Sở Nội vụ TP. Hà Nội','GRP001','Nhóm đối tượng 1','Đào Huy Hoàng','Nv','Nv','09232123212','hsa@gmail.com','','["BM-09", "BM-08", "BM-03"]','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0','34typck5duw0rogsgbm93b31w56wy62k','draft',NULL,'2026-07-01 08:03:33.251759','2026-07-01 09:11:37.909356',19,36,NULL),
 (3,'Hà Nội','GRP001','Nhóm đối tượng 1','Accounts1','1','2','3','hoanglc645@gmail.com','','["BM-09", "BM-08", "BM-03"]','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0','hso5pduj57t9st6jdt3xerwes29dlodo','draft',NULL,'2026-07-04 12:33:44.599267','2026-07-04 13:19:21.514302',22,36,NULL),
 (4,'','','','Test','','','0932342343','hoanglc645@gmail.com',NULL,'["BM-06", "BM-04", "BM-09", "BM-05", "BM-03", "BM-08", "BM-07"]','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0','0vums63pdx6mlivcuk6mlqi1bj7vw8m1','draft',NULL,'2026-07-04 14:58:28.460434','2026-07-04 14:58:28.481548',NULL,36,NULL),
 (5,'','','','test2','','','0922222222','test2@gmail.com',NULL,'["BM-03", "BM-08", "BM-09"]','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0','7wpe8p2fc3m69k14dz5zwcc1wo8greh2','draft',NULL,'2026-07-04 16:38:42.864339','2026-07-04 17:19:34.515048',NULL,36,NULL),
 (6,'Test','','','test','','Test','0933251123','123',NULL,'["BM-09", "BM-03", "BM-08"]','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0','7h757penye3vmdmh0ycn64hwztrrwebk','submitted','2026-07-05 06:46:10.923670','2026-07-05 06:44:40.730005','2026-07-05 06:46:10.923670',25,36,6),
 (7,'Test','','','test','','Test','0933251123','123',NULL,'["BM-09", "BM-03", "BM-08"]','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0','7h757penye3vmdmh0ycn64hwztrrwebk','draft',NULL,'2026-07-05 06:46:21.233785','2026-07-05 06:46:21.233785',NULL,36,6);
INSERT INTO "survey_surveyprogress" ("id","form_code","status","progress_percent","started_at","completed_at","last_accessed_at","created_at","participant_id","response_id","survey_id") VALUES (1,'BM-09','completed',0,'2026-07-01 09:04:56.331735','2026-07-01 11:31:14.846611','2026-07-01 11:38:17.050238','2026-07-01 09:04:15.897373',2,20,36),
 (2,'BM-08','not_started',0,NULL,NULL,'2026-07-01 09:04:15.915930','2026-07-01 09:04:15.910287',2,NULL,35),
 (3,'BM-03','in_progress',0,'2026-07-01 11:34:47.456521',NULL,'2026-07-01 11:38:17.072131','2026-07-01 09:04:15.921220',2,21,29),
 (4,'BM-09','in_progress',0,'2026-07-04 12:46:00.172384',NULL,'2026-07-04 13:17:43.488898','2026-07-04 12:33:44.676250',3,23,36),
 (5,'BM-08','not_started',0,NULL,NULL,'2026-07-04 12:33:44.706283','2026-07-04 12:33:44.697261',3,NULL,35),
 (6,'BM-06','not_started',0,NULL,NULL,'2026-07-04 12:33:44.723275','2026-07-04 12:33:44.712251',3,NULL,33),
 (7,'BM-04','not_started',0,NULL,NULL,'2026-07-04 12:33:44.741257','2026-07-04 12:33:44.730267',3,NULL,31),
 (8,'BM-03','not_started',0,NULL,NULL,'2026-07-04 13:17:43.515898','2026-07-04 13:17:43.505898',3,NULL,29),
 (9,'BM-06','not_started',0,NULL,NULL,'2026-07-04 14:58:28.498238','2026-07-04 14:58:28.498238',4,NULL,33),
 (10,'BM-04','not_started',0,NULL,NULL,'2026-07-04 14:58:28.507394','2026-07-04 14:58:28.507394',4,NULL,31),
 (11,'BM-09','not_started',0,NULL,NULL,'2026-07-04 14:58:28.516968','2026-07-04 14:58:28.516968',4,NULL,36),
 (12,'BM-05','not_started',0,NULL,NULL,'2026-07-04 14:58:28.526501','2026-07-04 14:58:28.526501',4,NULL,32),
 (13,'BM-03','not_started',0,NULL,NULL,'2026-07-04 14:58:28.534972','2026-07-04 14:58:28.534972',4,NULL,29),
 (14,'BM-08','not_started',0,NULL,NULL,'2026-07-04 14:58:28.542696','2026-07-04 14:58:28.542696',4,NULL,35),
 (15,'BM-07','not_started',0,NULL,NULL,'2026-07-04 14:58:28.552032','2026-07-04 14:58:28.552032',4,NULL,34),
 (16,'BM-03','in_progress',32,'2026-07-04 17:19:05.868804',NULL,'2026-07-05 06:13:35.226151','2026-07-04 16:38:42.877335',5,24,29),
 (17,'BM-08','not_started',0,NULL,NULL,'2026-07-04 16:38:42.892335','2026-07-04 16:38:42.892335',5,NULL,35),
 (18,'BM-09','not_started',0,NULL,NULL,'2026-07-04 16:38:42.902334','2026-07-04 16:38:42.902334',5,NULL,36),
 (19,'BM-09','completed',86,'2026-07-05 06:44:46.250375','2026-07-05 06:46:10.910657','2026-07-05 06:46:10.911654','2026-07-05 06:44:40.741021',6,25,36),
 (20,'BM-03','not_started',0,NULL,NULL,'2026-07-05 06:44:40.755021','2026-07-05 06:44:40.755021',6,NULL,29),
 (21,'BM-08','not_started',0,NULL,NULL,'2026-07-05 06:44:40.768008','2026-07-05 06:44:40.768008',6,NULL,35),
 (22,'BM-09','completed',0,'2026-07-05 06:46:28.313854','2026-07-05 06:46:33.825998','2026-07-05 07:38:47.082904','2026-07-05 06:46:21.251343',7,26,36),
 (23,'BM-03','completed',58,'2026-07-05 07:30:39.280260','2026-07-05 07:31:18.536507','2026-07-05 07:38:47.190891','2026-07-05 06:46:21.266342',7,28,29),
 (24,'BM-08','completed',79,'2026-07-05 07:30:01.745941','2026-07-05 07:30:27.815304','2026-07-05 07:38:47.273903','2026-07-05 06:46:21.279347',7,27,35);
INSERT INTO "survey_surveyunitstatus" ("id","status","completed_count","total_assignees","completed_at","updated_at","organization_id","survey_id") VALUES (1,'in_progress',1,2,NULL,'2026-07-05 07:12:16.578004',1,36),
 (2,'in_progress',1,2,NULL,'2026-07-05 07:30:27.858308',1,35),
 (3,'in_progress',1,2,NULL,'2026-07-05 07:31:18.585507',1,29);
CREATE INDEX IF NOT EXISTS "analytics_a_survey__9befcb_idx" ON "analytics_aggregatedresult" (
	"survey_id",
	"level",
	"entity_name"
);
CREATE INDEX IF NOT EXISTS "analytics_aggregatedresult_survey_id_7c8ee715" ON "analytics_aggregatedresult" (
	"survey_id"
);
CREATE UNIQUE INDEX IF NOT EXISTS "analytics_aggregatedresult_survey_id_level_entity_name_year_quarter_094979a6_uniq" ON "analytics_aggregatedresult" (
	"survey_id",
	"level",
	"entity_name",
	"year",
	"quarter"
);
CREATE INDEX IF NOT EXISTS "analytics_comparisonreport_survey_id_072a2dde" ON "analytics_comparisonreport" (
	"survey_id"
);
CREATE INDEX IF NOT EXISTS "analytics_scoringconfig_survey_id_8388cbe6" ON "analytics_scoringconfig" (
	"survey_id"
);
CREATE INDEX IF NOT EXISTS "analytics_targetgroup_surveys_survey_id_615de1a9" ON "analytics_targetgroup_surveys" (
	"survey_id"
);
CREATE INDEX IF NOT EXISTS "analytics_targetgroup_surveys_targetgroup_id_0a75863e" ON "analytics_targetgroup_surveys" (
	"targetgroup_id"
);
CREATE UNIQUE INDEX IF NOT EXISTS "analytics_targetgroup_surveys_targetgroup_id_survey_id_03c02e7e_uniq" ON "analytics_targetgroup_surveys" (
	"targetgroup_id",
	"survey_id"
);
CREATE UNIQUE INDEX IF NOT EXISTS "survey_blocklist_block_type_value_ee945a1b_uniq" ON "survey_blocklist" (
	"block_type",
	"value"
);
CREATE INDEX IF NOT EXISTS "survey_ques_compone_07dab6_idx" ON "survey_question" (
	"component_type"
);
CREATE INDEX IF NOT EXISTS "survey_question_question_type_id_aa3f05b2" ON "survey_question" (
	"question_type_id"
);
CREATE INDEX IF NOT EXISTS "survey_question_section_id_85e91c07" ON "survey_question" (
	"section_id"
);
CREATE INDEX IF NOT EXISTS "survey_resp_is_clea_29ef78_idx" ON "survey_response" (
	"is_cleaned",
	"is_duplicate"
);
CREATE INDEX IF NOT EXISTS "survey_resp_respond_addc01_idx" ON "survey_response" (
	"respondent_ip",
	"respondent_device_id"
);
CREATE INDEX IF NOT EXISTS "survey_resp_survey__5eac70_idx" ON "survey_response" (
	"survey_id",
	"submitted_at"
);
CREATE INDEX IF NOT EXISTS "survey_resp_survey__bc9fe9_idx" ON "survey_response" (
	"survey_id",
	"status"
);
CREATE INDEX IF NOT EXISTS "survey_response_survey_id_be749458" ON "survey_response" (
	"survey_id"
);
CREATE INDEX IF NOT EXISTS "survey_response_user_id_3e2a2e81" ON "survey_response" (
	"user_id"
);
CREATE INDEX IF NOT EXISTS "survey_section_survey_id_73b84f3b" ON "survey_section" (
	"survey_id"
);
CREATE UNIQUE INDEX IF NOT EXISTS "survey_section_survey_id_code_568d3dbf_uniq" ON "survey_section" (
	"survey_id",
	"code"
);
CREATE INDEX IF NOT EXISTS "survey_surv_organiz_a8ae25_idx" ON "survey_surveyunitstatus" (
	"organization_id",
	"status"
);
CREATE INDEX IF NOT EXISTS "survey_surv_slug_b1e903_idx" ON "survey_survey" (
	"slug",
	"status"
);
CREATE INDEX IF NOT EXISTS "survey_surv_survey__11b93f_idx" ON "survey_surveyparticipant" (
	"survey_id",
	"session_key"
);
CREATE INDEX IF NOT EXISTS "survey_surv_survey__5013f5_idx" ON "survey_surveyunitstatus" (
	"survey_id",
	"status"
);
CREATE INDEX IF NOT EXISTS "survey_surv_survey__ef19be_idx" ON "survey_surveyparticipant" (
	"survey_id",
	"email"
);
CREATE INDEX IF NOT EXISTS "survey_surv_survey__f9460a_idx" ON "survey_surveyparticipant" (
	"survey_id",
	"target_group_code"
);
CREATE INDEX IF NOT EXISTS "survey_survey_category_id_2d32ba53" ON "survey_survey" (
	"category_id"
);
CREATE INDEX IF NOT EXISTS "survey_surveyassignment_section_id_b7244ac9" ON "survey_surveyassignment" (
	"section_id"
);
CREATE INDEX IF NOT EXISTS "survey_surveyassignment_survey_id_6173e9fa" ON "survey_surveyassignment" (
	"survey_id"
);
CREATE UNIQUE INDEX IF NOT EXISTS "survey_surveyassignment_survey_id_form_code_target_group_code_e35871c4_uniq" ON "survey_surveyassignment" (
	"survey_id",
	"form_code",
	"target_group_code"
);
CREATE INDEX IF NOT EXISTS "survey_surveyparticipant_survey_id_87a3c21d" ON "survey_surveyparticipant" (
	"survey_id"
);
CREATE INDEX IF NOT EXISTS "survey_surveyparticipant_user_id_cb26c504" ON "survey_surveyparticipant" (
	"user_id"
);
CREATE INDEX IF NOT EXISTS "survey_surveyprogress_participant_id_34a833df" ON "survey_surveyprogress" (
	"participant_id"
);
CREATE UNIQUE INDEX IF NOT EXISTS "survey_surveyprogress_participant_id_form_code_bc8f7eb1_uniq" ON "survey_surveyprogress" (
	"participant_id",
	"form_code"
);
CREATE INDEX IF NOT EXISTS "survey_surveyprogress_survey_id_b01d90e3" ON "survey_surveyprogress" (
	"survey_id"
);
CREATE INDEX IF NOT EXISTS "survey_surveyunitstatus_organization_id_6d68266b" ON "survey_surveyunitstatus" (
	"organization_id"
);
CREATE INDEX IF NOT EXISTS "survey_surveyunitstatus_survey_id_8afa0fb4" ON "survey_surveyunitstatus" (
	"survey_id"
);
CREATE UNIQUE INDEX IF NOT EXISTS "survey_surveyunitstatus_survey_id_organization_id_71ad0385_uniq" ON "survey_surveyunitstatus" (
	"survey_id",
	"organization_id"
);
COMMIT;

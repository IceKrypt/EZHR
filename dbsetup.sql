CREATE DATABASE `job_schema` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */;

CREATE TABLE `jobs` (
  job_title varchar(255) NOT NULL,
  job_company varchar(45) NOT NULL,
  job_location varchar(70) NOT NULL,
  job_summary longtext
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;




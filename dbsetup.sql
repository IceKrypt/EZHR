CREATE TABLE `companies` (
  `company_name` varchar(255) NOT NULL,
  PRIMARY KEY (`company_name`)
);

CREATE TABLE `jobs` (
  `job_title` varchar(255) NOT NULL,
  `job_company` varchar(255) NOT NULL,
  `job_location` varchar(255) NOT NULL,
  `job_summary` text NOT NULL,
  `job_url` text NOT NULL

);

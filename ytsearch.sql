CREATE DATABASE ytsearch;
USE ytsearch;
CREATE TABLE `tbl_videos_metadata` (
  `video_id` varchar(500) NOT NULL,
  `title` varchar(500) NOT NULL,
  `description` text,
  `thumbnail_url` varchar(100) DEFAULT NULL,
  `duration` bigint(20) NOT NULL,
  `published_at` datetime NOT NULL,
  PRIMARY KEY (`video_id`)
);
-- NameGenerationAgent Navicat script (MySQL)
-- Navicat 连接名称建议: name_agent_mysql
-- 执行方式: 在 Navicat 查询窗口打开本文件 -> 点击“运行全部”

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 1) 创建数据库
CREATE DATABASE IF NOT EXISTS `name_generation_agent`
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE `name_generation_agent`;

-- 2) 创建应用用户（可选）
-- 说明: 如果当前账号无 CREATE USER/GRANT 权限，请保持注释，不影响建库建表。
-- CREATE USER IF NOT EXISTS 'name_agent_app'@'%' IDENTIFIED BY '123456';
-- GRANT ALL PRIVILEGES ON `name_generation_agent`.* TO 'name_agent_app'@'%';
-- FLUSH PRIVILEGES;

-- 3) users 表
CREATE TABLE IF NOT EXISTS `users` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `phone` VARCHAR(32) NOT NULL,
  `password_hash` VARCHAR(512) NOT NULL,
  `role` VARCHAR(20) NOT NULL DEFAULT 'user',
  `is_enabled` TINYINT(1) NOT NULL DEFAULT 1,
  `must_change_password` TINYINT(1) NOT NULL DEFAULT 0,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  `last_login_at` DATETIME NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_users_phone` (`phone`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4) user_tokens 表
CREATE TABLE IF NOT EXISTS `user_tokens` (
  `token` VARCHAR(200) NOT NULL,
  `user_id` BIGINT NOT NULL,
  `created_at` DATETIME NOT NULL,
  `expires_at` DATETIME NOT NULL,
  `revoked` TINYINT(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`token`),
  KEY `idx_user_tokens_user_id` (`user_id`),
  CONSTRAINT `fk_user_tokens_user_id`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5) generation_records 表
CREATE TABLE IF NOT EXISTS `generation_records` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT NOT NULL,
  `description` TEXT NOT NULL,
  `cultural_style` VARCHAR(64) NOT NULL,
  `gender` VARCHAR(32) NOT NULL,
  `age` VARCHAR(32) NOT NULL,
  `request_count` INT NOT NULL DEFAULT 1,
  `api_name` VARCHAR(100) NOT NULL DEFAULT '',
  `model` VARCHAR(200) NOT NULL DEFAULT '',
  `names_json` LONGTEXT NOT NULL,
  `created_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_generation_records_user_id` (`user_id`),
  KEY `idx_generation_records_created_at` (`created_at`),
  CONSTRAINT `fk_generation_records_user_id`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6) favorite_records 表
CREATE TABLE IF NOT EXISTS `favorite_records` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT NOT NULL,
  `favorite_uid` VARCHAR(120) NOT NULL,
  `name` VARCHAR(120) NOT NULL DEFAULT '',
  `meaning` TEXT NOT NULL,
  `style` VARCHAR(120) NOT NULL DEFAULT '',
  `gender` VARCHAR(60) NOT NULL DEFAULT '',
  `source` VARCHAR(120) NOT NULL DEFAULT '',
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_user_favorite_uid` (`user_id`, `favorite_uid`),
  KEY `idx_favorite_records_user_id` (`user_id`),
  KEY `idx_favorite_records_created_at` (`created_at`),
  CONSTRAINT `fk_favorite_records_user_id`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;

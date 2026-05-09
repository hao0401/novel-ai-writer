CREATE DATABASE IF NOT EXISTS novel_ai_writer DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE novel_ai_writer;

CREATE TABLE IF NOT EXISTS users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(50) NOT NULL UNIQUE,
  pen_name VARCHAR(80) NOT NULL DEFAULT '',
  password_hash VARCHAR(255) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS novels (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  title VARCHAR(120) NOT NULL,
  genre VARCHAR(40) NOT NULL DEFAULT '都市',
  style VARCHAR(80) NOT NULL DEFAULT '',
  target_platform VARCHAR(80) NOT NULL DEFAULT '',
  synopsis TEXT,
  tags VARCHAR(255) NOT NULL DEFAULT '',
  selling_points TEXT,
  status VARCHAR(30) NOT NULL DEFAULT '构思中',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_novels_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS characters (
  id INT PRIMARY KEY AUTO_INCREMENT,
  novel_id INT NOT NULL,
  name VARCHAR(80) NOT NULL,
  role_type VARCHAR(40) NOT NULL DEFAULT '主角',
  identity VARCHAR(120) NOT NULL DEFAULT '',
  personality TEXT,
  goal TEXT,
  ability TEXT,
  background TEXT,
  relation_to_protagonist VARCHAR(160) NOT NULL DEFAULT '',
  plot_function TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_characters_novel FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS world_settings (
  id INT PRIMARY KEY AUTO_INCREMENT,
  novel_id INT NOT NULL,
  world_background TEXT,
  era_environment TEXT,
  geography TEXT,
  organizations TEXT,
  hierarchy TEXT,
  power_system TEXT,
  important_rules TEXT,
  taboos TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_world_settings_novel FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS outlines (
  id INT PRIMARY KEY AUTO_INCREMENT,
  novel_id INT NOT NULL,
  outline_type VARCHAR(30) NOT NULL DEFAULT '章节大纲',
  volume_title VARCHAR(120) NOT NULL DEFAULT '',
  chapter_number INT NOT NULL DEFAULT 1,
  chapter_title VARCHAR(160) NOT NULL DEFAULT '',
  chapter_goal TEXT,
  main_plot TEXT,
  conflict TEXT,
  highlight TEXT,
  cliffhanger TEXT,
  expected_words INT NOT NULL DEFAULT 2000,
  content TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_outlines_novel FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chapters (
  id INT PRIMARY KEY AUTO_INCREMENT,
  novel_id INT NOT NULL,
  outline_id INT NULL,
  chapter_number INT NOT NULL DEFAULT 1,
  title VARCHAR(160) NOT NULL,
  content LONGTEXT,
  highlights TEXT,
  foreshadowing TEXT,
  summary TEXT,
  memory_keywords VARCHAR(255) NOT NULL DEFAULT '',
  status VARCHAR(30) NOT NULL DEFAULT '草稿',
  uploaded_platform VARCHAR(80) NOT NULL DEFAULT '',
  word_count INT NOT NULL DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_chapters_novel FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE,
  CONSTRAINT fk_chapters_outline FOREIGN KEY (outline_id) REFERENCES outlines(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS submission_records (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  novel_id INT NOT NULL,
  chapter_id INT NULL,
  platform VARCHAR(80) NOT NULL DEFAULT '番茄小说',
  status VARCHAR(30) NOT NULL DEFAULT '未整理',
  uploaded_at DATETIME NULL,
  platform_link VARCHAR(255) NOT NULL DEFAULT '',
  remarks TEXT,
  compiled_content LONGTEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_submission_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_submission_novel FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE,
  CONSTRAINT fk_submission_chapter FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS ai_generation_records (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  novel_id INT NULL,
  generation_type VARCHAR(40) NOT NULL,
  input_text LONGTEXT,
  output_text LONGTEXT,
  quality_score INT NOT NULL DEFAULT 0,
  quality_report TEXT,
  retry_count INT NOT NULL DEFAULT 0,
  ai_duration_ms INT NOT NULL DEFAULT 0,
  prompt_tokens INT NOT NULL DEFAULT 0,
  completion_tokens INT NOT NULL DEFAULT 0,
  total_tokens INT NOT NULL DEFAULT 0,
  ai_success INT NOT NULL DEFAULT 1,
  ai_error TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_ai_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_ai_novel FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS prompt_templates (
  id INT PRIMARY KEY AUTO_INCREMENT,
  task_type VARCHAR(40) NOT NULL,
  genre VARCHAR(40) NOT NULL DEFAULT '',
  name VARCHAR(120) NOT NULL DEFAULT '',
  system_prompt TEXT,
  user_template TEXT,
  enabled INT NOT NULL DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_prompt_task (task_type)
);

CREATE TABLE IF NOT EXISTS knowledge_items (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  novel_id INT NULL,
  title VARCHAR(160) NOT NULL,
  item_type VARCHAR(40) NOT NULL DEFAULT '素材',
  keywords VARCHAR(255) NOT NULL DEFAULT '',
  content LONGTEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_knowledge_user (user_id),
  INDEX idx_knowledge_novel (novel_id),
  CONSTRAINT fk_knowledge_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_knowledge_novel FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE
);

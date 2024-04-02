--Sample data for users table

INSERT INTO users (user_id, username, email_address, bio, profile_picture)
VALUES 
('f4qz3', 'Bhavesh', 'bhavesh@example.com', 'Music!!', '/path/to/profile_picture4.jpg');

-- Sample data for audio_files 


INSERT INTO audio_files (user_id, title, audio_file, like_count, created_at)
VALUES 
(1, 'Audio File 1', '/path/to/audio_file4.mp3', 7, '2024-03-24 13:00:00'),
(1, 'Audio File 2', '/path/to/audio_file5.mp3', 2, '2024-03-24 14:00:00'),
(1, 'Audio File 3', '/path/to/audio_file6.mp3', 8, '2024-03-24 15:00:00'),
(1, 'Audio File 4', '/path/to/audio_file7.mp3', 4, '2024-03-24 16:00:00'),
(1, 'Audio File 5', '/path/to/audio_file8.mp3', 6, '2024-03-24 17:00:00');

INSERT INTO audio_files (user_id, parent_audio_id, title, audio_file, like_count, created_at)
VALUES 
(1, NULL, 'Audio File 4', '/path/to/audio_file4.mp3', 7, '2024-03-24 13:00:00'),
(1, 11, 'Audio File 5', '/path/to/audio_file5.mp3', 2, '2024-03-24 14:00:00'),
(1, 12, 'Audio File 6', '/path/to/audio_file6.mp3', 8, '2024-03-24 15:00:00'),
(1, 13, 'Audio File 7', '/path/to/audio_file7.mp3', 4, '2024-03-24 16:00:00'),
(1, 11, 'Audio File 8', '/path/to/audio_file8.mp3', 6, '2024-03-24 17:00:00');

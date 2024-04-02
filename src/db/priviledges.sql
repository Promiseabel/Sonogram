CREATE USER 'user'@'localhost' IDENTIFIED BY 'sonogramuser';

GRANT SELECT, INSERT, UPDATE ON Sonogram.users TO 'user'@'localhost';
GRANT SELECT, INSERT, UPDATE ON Sonogram.audio_files TO 'user'@'localhost';

GRANT EXECUTE ON PROCEDURE AuthenticateUser TO 'user'@'localhost';

GRANT EXECUTE ON PROCEDURE CreateUser TO 'user'@'localhost';

GRANT EXECUTE ON PROCEDURE DeleteAudio TO 'user'@'localhost';

GRANT EXECUTE ON PROCEDURE EditLikeCount TO 'user'@'localhost';

GRANT EXECUTE ON PROCEDURE GetAudioFile TO 'user'@'localhost';

GRANT EXECUTE ON PROCEDURE GetUser TO 'user'@'localhost';

GRANT EXECUTE ON PROCEDURE GetUserID TO 'user'@'localhost';

GRANT EXECUTE ON PROCEDURE ListAllAudios TO 'user'@'localhost';

GRANT EXECUTE ON PROCEDURE ListAudioReplies TO 'user'@'localhost';

GRANT EXECUTE ON PROCEDURE ListUserAudios TO 'user'@'localhost';

GRANT EXECUTE ON PROCEDURE UpdateAudio TO 'user'@'localhost';

GRANT EXECUTE ON PROCEDURE UpdateUser TO 'user'@'localhost';

GRANT EXECUTE ON PROCEDURE UploadAudio TO 'user'@'localhost'; 

FLUSH PRIVILEGES;

SHOW GRANTS FOR 'user'@'localhost';
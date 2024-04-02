DELIMITER //

DROP PROCEDURE IF EXISTS CreateUser //

CREATE PROCEDURE CreateUser(
    IN p_username VARCHAR(25), 
    IN p_password VARCHAR(50),
    IN p_email_address VARCHAR(255), 
    IN p_bio VARCHAR(255),
    IN p_profile_picture VARCHAR(255)
)
BEGIN

    DECLARE salt NVARCHAR(36);
    SET salt = UUID();

    INSERT INTO users (username, passwordHash, salt, email_address, bio, profile_picture) 
    VALUES (p_username, SHA2(CONCAT(p_password,salt), 512), salt, p_email_address, p_bio, p_profile_picture);
END  //
DELIMITER ;

DELIMITER // 

DROP PROCEDURE IF EXISTS GetUserID // 

CREATE PROCEDURE GetUserID(IN p_username VARCHAR(25))
BEGIN
    SELECT user_id 
    FROM users
    WHERE username = p_username;
END//

DELIMITER ;
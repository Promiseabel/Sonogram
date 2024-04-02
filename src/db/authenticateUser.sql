
DELIMITER //

DROP PROCEDURE IF EXISTS AuthenticateUser // 

CREATE PROCEDURE AuthenticateUser(IN p_username VARCHAR(25), IN p_password VARCHAR(50))
BEGIN

    DECLARE var_user_id INT DEFAULT NULL;
    DECLARE var_salt NVARCHAR(36);
    DECLARE var_passwordHash VARCHAR(128);
    DECLARE isAuthenticated BOOLEAN;

    -- Attempt to retrieve the salt and password hash for the given username
    SELECT user_id, salt, passwordHash INTO var_user_id, var_salt, var_passwordHash
    FROM users 
    WHERE username = p_username
    LIMIT 1;

    -- If a user was found, compare the provided password (hashed with the user's salt) with the stored hash
    IF var_user_id IS NOT NULL THEN
        IF SHA2(CONCAT(p_password, var_salt), 512) = var_passwordHash THEN
            SET isAuthenticated = 1; -- Password matches
        ELSE
            SET isAuthenticated = 0; -- Incorrect password
        END IF;
    ELSE
        SET isAuthenticated = 0; -- User not found
    END IF;

    SELECT isAuthenticated AS Authenticated;
END //
DELIMITER ;

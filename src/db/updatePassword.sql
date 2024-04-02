DELIMITER //

DROP PROCEDURE IF EXISTS UpdatePassword // 

CREATE PROCEDURE UpdatePassword(IN p_user_id BIGINT UNSIGNED,IN p_old_password VARCHAR(50), IN p_new_password VARCHAR(50))
BEGIN

    DECLARE var_username VARCHAR(25) DEFAULT NULL;
    DECLARE var_salt NVARCHAR(36);
    DECLARE var_passwordHash VARCHAR(128);
    DECLARE isApproved BOOLEAN;

    -- Attempt to retrieve the salt and password hash for the given username
    SELECT username, salt, passwordHash INTO var_username, var_salt, var_passwordHash
    FROM users 
    WHERE user_id = p_user_id
    LIMIT 1;

    -- If a user was found, compare the provided password (hashed with the user's salt) with the stored hash
    IF var_username IS NOT NULL THEN
        IF SHA2(CONCAT(p_old_password, var_salt), 512) = var_passwordHash THEN
            SET isApproved = 1; -- Password matches
            UPDATE users SET passwordHash = SHA2(CONCAT(p_new_password,salt), 512) WHERE user_id = p_user_id;
        ELSE
            SET isApproved = 0; -- Incorrect password
        END IF;
    ELSE
        SET isApproved = 0; -- User not found
    END IF;

    SELECT isApproved AS Approved;

END //
DELIMITER ;
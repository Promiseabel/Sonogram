DELIMITER //

DROP PROCEDURE IF EXISTS DeleteAudio // 

CREATE PROCEDURE DeleteAudio(IN p_audio_id BIGINT UNSIGNED)
BEGIN
        UPDATE audio_files SET deleted = TRUE WHERE (audio_id = p_audio_id AND parent_audio_id = p_audio_id);

END //
DELIMITER ;

BEGIN;
    -- tbl_Rollen
    SELECT COUNT(*) FROM `tbl_Rollen` WHERE LEFT(`rollenname`, 17) = "Technischer User:";
    SELECT COUNT(*) FROM `tbl_Rollen` WHERE LEFT(`rollenname`, 4) = "NPU:";
    Update `tbl_Rollen` SET rollenname = REPLACE(`rollenname`, "Technischer User:", "NPU:")
        WHERE LEFT(`rollenname`, 17) = "Technischer User:";
    SELECT COUNT(*) FROM `tbl_Rollen` WHERE LEFT(`rollenname`, 17) = "Technischer User:";
    SELECT COUNT(*) FROM `tbl_Rollen` WHERE LEFT(`rollenname`, 4) = "NPU:";

    -- tbl_RolleHatAF
    SELECT "tbl_RolleHatAF";
    SELECT COUNT(*) FROM `tbl_RolleHatAF` WHERE LEFT(`rollenname`, 17) = "Technischer User:";
    SELECT COUNT(*) FROM `tbl_RolleHatAF` WHERE LEFT(`rollenname`, 4) = "NPU:";
    Update `tbl_RolleHatAF` SET rollenname = REPLACE(`rollenname`, "Technischer User:", "NPU:")
        WHERE LEFT(`rollenname`, 17) = "Technischer User:";
    SELECT COUNT(*) FROM `tbl_RolleHatAF` WHERE LEFT(`rollenname`, 17) = "Technischer User:";
    SELECT COUNT(*) FROM `tbl_RolleHatAF` WHERE LEFT(`rollenname`, 4) = "NPU:";

    -- tbl_UserHatRolle
    SELECT "tbl_UserHatRolle";
    SELECT COUNT(*) FROM `tbl_UserHatRolle` WHERE LEFT(`rollenname`, 17) = "Technischer User:";
    SELECT COUNT(*) FROM `tbl_UserHatRolle` WHERE LEFT(`rollenname`, 4) = "NPU:";
    Update `tbl_UserHatRolle` SET rollenname = REPLACE(`rollenname`, "Technischer User:", "NPU:")
        WHERE LEFT(`rollenname`, 17) = "Technischer User:";
    SELECT COUNT(*) FROM `tbl_UserHatRolle` WHERE LEFT(`rollenname`, 17) = "Technischer User:";
    SELECT COUNT(*) FROM `tbl_UserHatRolle` WHERE LEFT(`rollenname`, 4) = "NPU:";

ROLLBACK;

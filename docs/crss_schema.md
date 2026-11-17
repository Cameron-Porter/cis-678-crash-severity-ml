# CRSS raw CSV schemas, 2020–2024

Built from our local `data/raw/<YEAR>/` files using `python src/data/document_raw.py`.
The script does not download data or read the processed splits.
See [data/README.md](../data/README.md) for sources, keys, and setup.

The [inventory](crss_inventory.csv) lists row counts, column counts, sizes, hashes,
and source URLs. We calculate the hashes from our local files so teammates can
compare copies. NHTSA did not supply these hashes.

Each section starts with the 2020 columns in file order, then lists changes from
the previous year. Added columns use the new year's order; removed columns use
the previous year's order. Order checks compare columns present in both years.

This report checks columns. We will review code meanings and missing codes in
DATA-04. CSV files do not specify data types; use the NHTSA manuals linked in
the README to check what each field and code means.

## Core table sizes

| Year | Table | Rows | Columns |
|---|---|---:|---:|
| 2020 | accident.csv | 54,745 | 80 |
| 2020 | person.csv | 131,962 | 108 |
| 2020 | vehicle.csv | 94,718 | 167 |
| 2021 | accident.csv | 54,200 | 80 |
| 2021 | person.csv | 133,734 | 108 |
| 2021 | vehicle.csv | 95,785 | 167 |
| 2022 | accident.csv | 53,955 | 80 |
| 2022 | person.csv | 132,175 | 112 |
| 2022 | vehicle.csv | 94,756 | 167 |
| 2023 | accident.csv | 50,103 | 80 |
| 2023 | person.csv | 122,388 | 112 |
| 2023 | vehicle.csv | 87,461 | 169 |
| 2024 | accident.csv | 51,658 | 80 |
| 2024 | person.csv | 126,159 | 112 |
| 2024 | vehicle.csv | 90,641 | 167 |

## accident.csv

2020 columns:

```text
CASENUM, STRATUM, STRATUMNAME, REGION, REGIONNAME, PSU, PJ, PSU_VAR, URBANICITY, URBANICITYNAME, VE_TOTAL, VE_FORMS, PVH_INVL, PEDS, PERMVIT, PERNOTMVIT, NUM_INJ, NUM_INJNAME, MONTH, MONTHNAME, YEAR, YEARNAME, DAY_WEEK, DAY_WEEKNAME, HOUR, HOURNAME, MINUTE, MINUTENAME, HARM_EV, HARM_EVNAME, ALCOHOL, ALCOHOLNAME, MAX_SEV, MAX_SEVNAME, MAN_COLL, MAN_COLLNAME, RELJCT1, RELJCT1NAME, RELJCT2, RELJCT2NAME, TYP_INT, TYP_INTNAME, WRK_ZONE, WRK_ZONENAME, REL_ROAD, REL_ROADNAME, LGT_COND, LGT_CONDNAME, SCH_BUS, SCH_BUSNAME, INT_HWY, INT_HWYNAME, WEATHER, WEATHERNAME, WKDY_IM, WKDY_IMNAME, HOUR_IM, HOUR_IMNAME, MINUTE_IM, MINUTE_IMNAME, EVENT1_IM, EVENT1_IMNAME, MANCOL_IM, MANCOL_IMNAME, RELJCT1_IM, RELJCT1_IMNAME, RELJCT2_IM, RELJCT2_IMNAME, LGTCON_IM, LGTCON_IMNAME, WEATHR_IM, WEATHR_IMNAME, MAXSEV_IM, MAXSEV_IMNAME, NO_INJ_IM, NO_INJ_IMNAME, ALCHL_IM, ALCHL_IMNAME, PSUSTRAT, WEIGHT
```

| Year | Added columns | Removed columns | Shared column order changed? |
|---|---|---|---|
| 2021 | None | None | Yes |
| 2022 | None | None | No |
| 2023 | None | None | No |
| 2024 | None | None | No |

## cevent.csv

2020 columns:

```text
CASENUM, REGION, REGIONNAME, PSU, PJ, PSU_VAR, URBANICITY, URBANICITYNAME, STRATUM, STRATUMNAME, EVENTNUM, VNUMBER1, AOI1, AOI1NAME, SOE, SOENAME, VNUMBER2, VNUMBER2NAME, AOI2, AOI2NAME, PSUSTRAT, WEIGHT
```

| Year | Added columns | Removed columns | Shared column order changed? |
|---|---|---|---|
| 2021 | None | None | No |
| 2022 | None | None | No |
| 2023 | None | None | Yes |
| 2024 | None | None | No |

## crashrf.csv

2020 columns:

```text
CASENUM, STRATUM, STRATUMNAME, REGION, REGIONNAME, PSU, PJ, PSU_VAR, URBANICITY, URBANICITYNAME, CRASHRF, CRASHRFNAME, PSUSTRAT, WEIGHT
```

| Year | Added columns | Removed columns | Shared column order changed? |
|---|---|---|---|
| 2021 | None | None | No |
| 2022 | None | None | No |
| 2023 | None | None | Yes |
| 2024 | None | None | No |

## damage.csv

2020 columns:

```text
CASENUM, VEH_NO, STRATUM, STRATUMNAME, REGION, REGIONNAME, PSU, PJ, PSU_VAR, URBANICITY, URBANICITYNAME, DAMAGE, DAMAGENAME, PSUSTRAT, WEIGHT
```

| Year | Added columns | Removed columns | Shared column order changed? |
|---|---|---|---|
| 2021 | None | None | No |
| 2022 | None | None | No |
| 2023 | None | None | Yes |
| 2024 | None | None | No |

## distract.csv

2020 columns:

```text
CASENUM, VEH_NO, STRATUM, STRATUMNAME, REGION, REGIONNAME, PSU, PJ, PSU_VAR, URBANICITY, URBANICITYNAME, DRDISTRACT, DRDISTRACTNAME, PSUSTRAT, WEIGHT
```

| Year | Added columns | Removed columns | Shared column order changed? |
|---|---|---|---|
| 2021 | None | None | No |
| 2022 | None | None | No |
| 2023 | None | None | Yes |
| 2024 | None | None | No |

## drimpair.csv

2020 columns:

```text
CASENUM, VEH_NO, STRATUM, STRATUMNAME, REGION, REGIONNAME, PSU, PJ, PSU_VAR, URBANICITY, URBANICITYNAME, DRIMPAIR, DRIMPAIRNAME, PSUSTRAT, WEIGHT
```

| Year | Added columns | Removed columns | Shared column order changed? |
|---|---|---|---|
| 2021 | None | None | No |
| 2022 | None | None | No |
| 2023 | None | None | Yes |
| 2024 | None | None | No |

## driverrf.csv

2020 columns:

```text
CASENUM, VEH_NO, STRATUM, STRATUMNAME, REGION, REGIONNAME, PSU, PJ, PSU_VAR, URBANICITY, URBANICITYNAME, DRIVERRF, DRIVERRFNAME, PSUSTRAT, WEIGHT
```

| Year | Added columns | Removed columns | Shared column order changed? |
|---|---|---|---|
| 2021 | None | None | No |
| 2022 | None | None | No |
| 2023 | None | None | Yes |
| 2024 | None | None | No |

## factor.csv

2020 columns:

```text
CASENUM, VEH_NO, STRATUM, STRATUMNAME, REGION, REGIONNAME, PSU, PJ, PSU_VAR, URBANICITY, URBANICITYNAME, VEHICLECC, VEHICLECCNAME, PSUSTRAT, WEIGHT
```

| Year | Added columns | Removed columns | Shared column order changed? |
|---|---|---|---|
| 2021 | None | None | No |
| 2022 | None | None | No |
| 2023 | None | None | Yes |
| 2024 | None | None | No |

## maneuver.csv

2020 columns:

```text
CASENUM, VEH_NO, STRATUM, STRATUMNAME, REGION, REGIONNAME, PSU, PJ, PSU_VAR, URBANICITY, URBANICITYNAME, MANEUVER, MANEUVERNAME, PSUSTRAT, WEIGHT
```

| Year | Added columns | Removed columns | Shared column order changed? |
|---|---|---|---|
| 2021 | None | None | No |
| 2022 | None | None | No |
| 2023 | None | None | Yes |
| 2024 | None | None | No |

## nmcrash.csv

2020 columns:

```text
CASENUM, VEH_NO, PER_NO, STRATUM, STRATUMNAME, REGION, REGIONNAME, PSU, PJ, PSU_VAR, URBANICITY, URBANICITYNAME, NMCC, NMCCNAME, PSUSTRAT, WEIGHT
```

| Year | Added columns | Removed columns | Shared column order changed? |
|---|---|---|---|
| 2021 | None | None | No |
| 2022 | None | None | No |
| 2023 | None | None | Yes |
| 2024 | None | None | No |

## nmdistract.csv

2020 columns:

```text
CASENUM, VEH_NO, PER_NO, STRATUM, STRATUMNAME, REGION, REGIONNAME, PSU, PJ, PSU_VAR, URBANICITY, URBANICITYNAME, NMDISTRACT, NMDISTRACTNAME, PSUSTRAT, WEIGHT
```

| Year | Added columns | Removed columns | Shared column order changed? |
|---|---|---|---|
| 2021 | None | None | No |
| 2022 | None | None | No |
| 2023 | None | None | Yes |
| 2024 | None | None | No |

## nmimpair.csv

2020 columns:

```text
CASENUM, VEH_NO, PER_NO, STRATUM, STRATUMNAME, REGION, REGIONNAME, PSU, PJ, PSU_VAR, URBANICITY, URBANICITYNAME, NMIMPAIR, NMIMPAIRNAME, PSUSTRAT, WEIGHT
```

| Year | Added columns | Removed columns | Shared column order changed? |
|---|---|---|---|
| 2021 | None | None | No |
| 2022 | None | None | No |
| 2023 | None | None | Yes |
| 2024 | None | None | No |

## nmprior.csv

2020 columns:

```text
CASENUM, VEH_NO, PER_NO, STRATUM, STRATUMNAME, REGION, REGIONNAME, PSU, PJ, PSU_VAR, URBANICITY, URBANICITYNAME, NMACTION, NMACTIONNAME, PSUSTRAT, WEIGHT
```

| Year | Added columns | Removed columns | Shared column order changed? |
|---|---|---|---|
| 2021 | None | None | No |
| 2022 | None | None | No |
| 2023 | None | None | Yes |
| 2024 | None | None | No |

## parkwork.csv

2020 columns:

```text
CASENUM, VEH_NO, STRATUM, STRATUMNAME, REGION, REGIONNAME, PSU, PJ, PSU_VAR, URBANICITY, URBANICITYNAME, PVE_FORMS, PNUMOCCS, PNUMOCCSNAME, PMONTH, PMONTHNAME, PHOUR, PHOURNAME, PMINUTE, PMINUTENAME, PHARM_EV, PHARM_EVNAME, PMAN_COLL, PMAN_COLLNAME, PTYPE, PTYPENAME, PHIT_RUN, PHIT_RUNNAME, PMAKE, PMAKENAME, PMODEL, PMAK_MOD, PMAK_MODNAME, PBODYTYP, PBODYTYPNAME, PMODYEAR, PMODYEARNAME, PVIN, PVINNAME, PTRAILER, PTRAILERNAME, PMCARR_I1, PMCARR_I1NAME, PMCARR_I2, PMCARR_I2NAME, PMCARR_ID, PMCARR_IDNAME, PV_CONFIG, PV_CONFIGNAME, PCARGTYP, PCARGTYPNAME, PHAZ_INV, PHAZ_INVNAME, PHAZPLAC, PHAZPLACNAME, PHAZ_ID, PHAZ_IDNAME, PHAZ_CNO, PHAZ_CNONAME, PHAZ_REL, PHAZ_RELNAME, PBUS_USE, PBUS_USENAME, PSP_USE, PSP_USENAME, PEM_USE, PEM_USENAME, PIMPACT1, PIMPACT1NAME, PVEH_SEV, PVEH_SEVNAME, PTOWED, PTOWEDNAME, PM_HARM, PM_HARMNAME, PFIRE, PFIRENAME, PTRLR1VIN, PTRLR1VINNAME, PTRLR2VIN, PTRLR2VINNAME, PTRLR3VIN, PTRLR3VINNAME, PVPICMAKE, PVPICMAKENAME, PVPICMODEL, PVPICMODELNAME, PVPICBODYCLASS, PVPICBODYCLASSNAME, PICFINALBODY, PICFINALBODYNAME, PGVWR_FROM, PGVWR_FROMNAME, PGVWR_TO, PGVWR_TONAME, PTRLR1GVWR, PTRLR1GVWRNAME, PTRLR2GVWR, PTRLR2GVWRNAME, PTRLR3GVWR, PTRLR3GVWRNAME, PSUSTRAT, WEIGHT
```

| Year | Added columns | Removed columns | Shared column order changed? |
|---|---|---|---|
| 2021 | `PUNDEROVERRIDE`, `PUNDEROVERRIDENAME` | None | Yes |
| 2022 | None | None | No |
| 2023 | None | None | No |
| 2024 | None | None | No |

## pbtype.csv

2020 columns:

```text
CASENUM, VEH_NO, PER_NO, STRATUM, STRATUMNAME, REGION, REGIONNAME, PSU, PJ, PSU_VAR, URBANICITY, URBANICITYNAME, PBPTYPE, PBPTYPENAME, PBAGE, PBAGENAME, PBSEX, PBSEXNAME, PBCWALK, PBCWALKNAME, PBSWALK, PBSWALKNAME, PBSZONE, PBSZONENAME, PEDCTYPE, PEDCTYPENAME, BIKECTYPE, BIKECTYPENAME, PEDLOC, PEDLOCNAME, BIKELOC, BIKELOCNAME, PEDPOS, PEDPOSNAME, BIKEPOS, BIKEPOSNAME, PEDDIR, PEDDIRNAME, BIKEDIR, BIKEDIRNAME, MOTDIR, MOTDIRNAME, MOTMAN, MOTMANNAME, PEDLEG, PEDLEGNAME, PEDSNR, PEDSNRNAME, PEDCGP, PEDCGPNAME, BIKECGP, BIKECGPNAME, PSUSTRAT, WEIGHT
```

| Year | Added columns | Removed columns | Shared column order changed? |
|---|---|---|---|
| 2021 | None | None | Yes |
| 2022 | None | None | No |
| 2023 | None | None | No |
| 2024 | None | None | No |

## person.csv

2020 columns:

```text
CASENUM, VE_FORMS, VEH_NO, PER_NO, STRATUM, STRATUMNAME, REGION, REGIONNAME, PSU, PJ, PSU_VAR, URBANICITY, URBANICITYNAME, STR_VEH, MONTH, MONTHNAME, HOUR, HOURNAME, MINUTE, MINUTENAME, HARM_EV, HARM_EVNAME, MAN_COLL, MAN_COLLNAME, SCH_BUS, SCH_BUSNAME, MAKE, MAKENAME, MAK_MOD, MAK_MODNAME, BODY_TYP, BODY_TYPNAME, MOD_YEAR, MOD_YEARNAME, TOW_VEH, TOW_VEHNAME, SPEC_USE, SPEC_USENAME, EMER_USE, EMER_USENAME, ROLLOVER, ROLLOVERNAME, IMPACT1, IMPACT1NAME, FIRE_EXP, FIRE_EXPNAME, AGE, AGENAME, SEX, SEXNAME, PER_TYP, PER_TYPNAME, INJ_SEV, INJ_SEVNAME, SEAT_POS, SEAT_POSNAME, REST_USE, REST_USENAME, HELM_USE, HELM_USENAME, HELM_MIS, HELM_MISNAME, REST_MIS, REST_MISNAME, AIR_BAG, AIR_BAGNAME, EJECTION, EJECTIONNAME, DRINKING, DRINKINGNAME, ALC_STATUS, ALC_STATUSNAME, ATST_TYP, ATST_TYPNAME, ALC_RES, ALC_RESNAME, DRUGS, DRUGSNAME, HOSPITAL, HOSPITALNAME, LOCATION, LOCATIONNAME, VPICMAKE, VPICMAKENAME, VPICMODEL, VPICMODELNAME, VPICBODYCLASS, VPICBODYCLASSNAME, ICFINALBODY, ICFINALBODYNAME, SEX_IM, SEX_IMNAME, INJSEV_IM, INJSEV_IMNAME, EJECT_IM, EJECT_IMNAME, PERALCH_IM, PERALCH_IMNAME, SEAT_IM, SEAT_IMNAME, AGE_IM, AGE_IMNAME, PSUSTRAT, WEIGHT, GVWR_FROM, GVWR_FROMNAME, GVWR_TO, GVWR_TONAME
```

| Year | Added columns | Removed columns | Shared column order changed? |
|---|---|---|---|
| 2021 | None | None | Yes |
| 2022 | `DEVTYPE`, `DEVTYPENAME`, `DEVMOTOR`, `DEVMOTORNAME` | None | No |
| 2023 | None | None | Yes |
| 2024 | None | None | Yes |

## personrf.csv

2020 columns:

```text
CASENUM, VEH_NO, PER_NO, STRATUM, STRATUMNAME, REGION, REGIONNAME, PSU, PJ, PSU_VAR, URBANICITY, URBANICITYNAME, PERSONRF, PERSONRFNAME, PSUSTRAT, WEIGHT
```

| Year | Added columns | Removed columns | Shared column order changed? |
|---|---|---|---|
| 2021 | None | None | No |
| 2022 | None | None | No |
| 2023 | None | None | Yes |
| 2024 | None | None | No |

## pvehiclesf.csv

2020 columns:

```text
CASENUM, VEH_NO, STRATUM, STRATUMNAME, REGION, REGIONNAME, PSU, PJ, PSU_VAR, URBANICITY, URBANICITYNAME, PVEHICLESF, PVEHICLESFNAME, PSUSTRAT, WEIGHT
```

| Year | Added columns | Removed columns | Shared column order changed? |
|---|---|---|---|
| 2021 | None | None | No |
| 2022 | None | None | No |
| 2023 | None | None | Yes |
| 2024 | None | None | No |

## safetyeq.csv

2020 columns:

```text
CASENUM, VEH_NO, PER_NO, STRATUM, STRATUMNAME, REGION, REGIONNAME, PSU, PJ, PSU_VAR, URBANICITY, URBANICITYNAME, NMHELMET, NMHELMETNAME, NMPROPAD, NMPROPADNAME, NMOTHPRO, NMOTHPRONAME, NMREFCLO, NMREFCLONAME, NMLIGHT, NMLIGHTNAME, NMOTHPRE, NMOTHPRENAME, PSUSTRAT, WEIGHT
```

| Year | Added columns | Removed columns | Shared column order changed? |
|---|---|---|---|
| 2021 | None | None | No |
| 2022 | None | None | No |
| 2023 | None | None | Yes |
| 2024 | None | None | No |

## vehicle.csv

2020 columns:

```text
CASENUM, VEH_NO, STRATUM, STRATUMNAME, REGION, REGIONNAME, PSU, PJ, PSU_VAR, URBANICITY, URBANICITYNAME, VE_FORMS, NUMOCCS, NUMOCCSNAME, MONTH, MONTHNAME, HOUR, HOURNAME, MINUTE, MINUTENAME, HARM_EV, HARM_EVNAME, MAN_COLL, MAN_COLLNAME, UNITTYPE, UNITTYPENAME, HIT_RUN, HIT_RUNNAME, MAKE, MAKENAME, MODEL, MAK_MOD, MAK_MODNAME, BODY_TYP, BODY_TYPNAME, MOD_YEAR, MOD_YEARNAME, VIN, VINNAME, TOW_VEH, TOW_VEHNAME, J_KNIFE, J_KNIFENAME, MCARR_I1, MCARR_I1NAME, MCARR_I2, MCARR_I2NAME, MCARR_ID, MCARR_IDNAME, V_Config, V_ConfigNAME, CARGO_BT, CARGO_BTNAME, HAZ_INV, HAZ_INVNAME, HAZ_PLAC, HAZ_PLACNAME, HAZ_ID, HAZ_IDNAME, HAZ_CNO, HAZ_CNONAME, HAZ_REL, HAZ_RELNAME, BUS_USE, BUS_USENAME, SPEC_USE, SPEC_USENAME, EMER_USE, EMER_USENAME, TRAV_SP, TRAV_SPNAME, ROLLOVER, ROLLOVERNAME, ROLINLOC, ROLINLOCNAME, IMPACT1, IMPACT1NAME, DEFORMED, DEFORMEDNAME, TOWED, TOWEDNAME, M_HARM, M_HARMNAME, VEH_ALCH, VEH_ALCHNAME, MAX_VSEV, MAX_VSEVNAME, NUM_INJV, NUM_INJVNAME, FIRE_EXP, FIRE_EXPNAME, DR_PRES, DR_PRESNAME, DR_ZIP, DR_ZIPNAME, SPEEDREL, SPEEDRELNAME, VTRAFWAY, VTRAFWAYNAME, VNUM_LAN, VNUM_LANNAME, VSPD_LIM, VSPD_LIMNAME, VALIGN, VALIGNNAME, VPROFILE, VPROFILENAME, VSURCOND, VSURCONDNAME, VTRAFCON, VTRAFCONNAME, VTCONT_F, VTCONT_FNAME, P_CRASH1, P_CRASH1NAME, P_CRASH2, P_CRASH2NAME, P_CRASH3, P_CRASH3NAME, PCRASH4, PCRASH4NAME, PCRASH5, PCRASH5NAME, ACC_TYPE, ACC_TYPENAME, TRLR1VIN, TRLR1VINNAME, TRLR2VIN, TRLR2VINNAME, TRLR3VIN, TRLR3VINNAME, VPICMAKE, VPICMAKENAME, VPICMODEL, VPICMODELNAME, VPICBODYCLASS, VPICBODYCLASSNAME, ICFINALBODY, ICFINALBODYNAME, GVWR_FROM, GVWR_FROMNAME, GVWR_TO, GVWR_TONAME, TRLR1GVWR, TRLR1GVWRNAME, TRLR2GVWR, TRLR2GVWRNAME, TRLR3GVWR, TRLR3GVWRNAME, BDYTYP_IM, BDYTYP_IMNAME, MDLYR_IM, MDLYR_IMNAME, IMPACT1_IM, IMPACT1_IMNAME, VEVENT_IM, VEVENT_IMNAME, PCRASH1_IM, PCRASH1_IMNAME, MXVSEV_IM, MXVSEV_IMNAME, NUMINJ_IM, NUMINJ_IMNAME, V_ALCH_IM, V_ALCH_IMNAME, PSUSTRAT, WEIGHT
```

| Year | Added columns | Removed columns | Shared column order changed? |
|---|---|---|---|
| 2021 | `V_CONFIG`, `V_CONFIGNAME`, `UNDEROVERRIDE`, `UNDEROVERRIDENAME` | `V_Config`, `V_ConfigNAME`, `BDYTYP_IM`, `BDYTYP_IMNAME` | Yes |
| 2022 | `V_Config`, `V_ConfigNAME` | `V_CONFIG`, `V_CONFIGNAME` | Yes |
| 2023 | `ACC_CONFIG`, `ACC_CONFIGNAME` | None | No |
| 2024 | `V_CONFIG`, `V_CONFIGNAME` | `V_Config`, `V_ConfigNAME`, `ACC_CONFIG`, `ACC_CONFIGNAME` | No |

## vehiclesf.csv

2020 columns:

```text
CASENUM, VEH_NO, STRATUM, STRATUMNAME, REGION, REGIONNAME, PSU, PJ, PSU_VAR, URBANICITY, URBANICITYNAME, VEHICLESF, VEHICLESFNAME, PSUSTRAT, WEIGHT
```

| Year | Added columns | Removed columns | Shared column order changed? |
|---|---|---|---|
| 2021 | None | None | No |
| 2022 | None | None | No |
| 2023 | None | None | Yes |
| 2024 | None | None | No |

## vevent.csv

2020 columns:

```text
CASENUM, EventNum, VEH_NO, STRATUM, STRATUMNAME, REGION, REGIONNAME, PSU, PJ, PSU_VAR, URBANICITY, URBANICITYNAME, VEventNum, VNumber1, AOI1, AOI1NAME, SOE, SOENAME, VNumber2, VNumber2NAME, AOI2, AOI2NAME, PSUSTRAT, WEIGHT
```

| Year | Added columns | Removed columns | Shared column order changed? |
|---|---|---|---|
| 2021 | `EVENTNUM`, `VEVENTNUM`, `VNUMBER1`, `VNUMBER2`, `VNUMBER2NAME` | `EventNum`, `VEventNum`, `VNumber1`, `VNumber2`, `VNumber2NAME` | No |
| 2022 | `VNumber2`, `VNumber2NAME` | `VNUMBER2`, `VNUMBER2NAME` | No |
| 2023 | None | None | Yes |
| 2024 | None | None | No |

## violatn.csv

2020 columns:

```text
CASENUM, VEH_NO, STRATUM, STRATUMNAME, REGION, REGIONNAME, PSU, PJ, PSU_VAR, URBANICITY, URBANICITYNAME, VIOLATION, VIOLATIONNAME, PSUSTRAT, WEIGHT
```

| Year | Added columns | Removed columns | Shared column order changed? |
|---|---|---|---|
| 2021 | None | None | No |
| 2022 | None | None | No |
| 2023 | None | None | Yes |
| 2024 | None | None | No |

## vision.csv

2020 columns:

```text
CASENUM, VEH_NO, STRATUM, STRATUMNAME, REGION, REGIONNAME, PSU, PJ, PSU_VAR, URBANICITY, URBANICITYNAME, VISION, VISIONNAME, PSUSTRAT, WEIGHT
```

| Year | Added columns | Removed columns | Shared column order changed? |
|---|---|---|---|
| 2021 | None | None | No |
| 2022 | None | None | No |
| 2023 | None | None | Yes |
| 2024 | None | None | No |

## vpicdecode.csv

2020 columns:

```text
CASENUM, VEH_NO, VehicleDescriptor, VINDecodedOn, VINDecodeError, VehicleTypeId, VehicleType, ManufacturerFullNameId, ManufacturerFullName, MakeId, Make, ModelId, Model, ModelYear, Series, Trim, Series2, Trim2, PlantCountryId, PlantCountry, PlantState, PlantCity, PlantCompanyName, DestinationMarketId, DestinationMarket, BasePrice, Note, BodyClassId, BodyClass, DoorsCount, Windows, WheelBaseTypeId, WheelBaseType, TrackWidthIN, GrossVehicleWeightRatingFromId, GrossVehicleWeightRatingFrom, GrossVehicleWeightRatingToId, GrossVehicleWeightRatingTo, GrossCombWeightRatingFromId, GrossCombWeightRatingFrom, GrossCombWeightRatingToId, GrossCombWeightRatingTo, CurbWeightLB, WheelBaseIN_from, WheelBaseIN_To, WheelsCount, WheelSizeFrontIN, WheelSizeRearIN, TruckBodyCabTypeId, TruckBodyCabType, TruckBedTypeId, TruckBedType, TruckBedLengthIN, BusTypeId, BusType, BusFloorConfigurationTypeId, BusFloorConfigurationType, BusLengthFT, OtherBusInfo, CustomMotorcycleTypeId, CustomMotorcycleType, MotorcycleSuspensionTypeId, MotorcycleSuspensionType, MotorcycleChassisTypeId, MotorcycleChassisType, OtherMotorcycleInfo, SteeringLocationId, SteeringLocation, EntertainmentSystemId, EntertainmentSystem, SeatsCount, SeatRowsCount, TransmissionSpeeds, TransmissionStyleId, TransmissionStyle, DriveTypeId, DriveType, AxlesCount, AxleConfigurationId, AxleConfiguration, BrakeSystemTypeId, BrakeSystemType, BrakeSystemDesc, EVDriveUnitId, EVDriveUnit, BatteryKWh_From, BatteryKWh_to, BatteryV_From, BatteryV_to, BatteryA_From, BatteryA_to, BatteryPacksPerVehicle, BatteryModulesPerPack, BatteryCellsPerModule, BatteryTypeId, BatteryType, OtherBatteryInfo, ChargerLevelId, ChargerLevel, ChargerPowerKW, EngineManufacturer, EngineModel, EngineConfigurationId, EngineConfiguration, EnginePowerKW, EngineStrokeCycles, EngineCylindersCount, EngineBrakeHP_From, EngineBrakeHP_To, EngineCoolingTypeId, EngineCoolingType, DisplacementCI, DisplacementCC, DisplacementL, FuelTypePrimaryId, FuelTypePrimary, FuelTypeSecondaryId, FuelTypeSecondary, FuelDeliveryInjectionTypeId, FuelDeliveryInjectionType, EngineValveTrainDesignId, EngineValveTrainDesign, EngineElectrificationLevelId, EngineElectrificationLevel, EngineTurboId, EngineTurbo, TopSpeedMPH, OtherEngineInfo, SeatBeltTypeId, SeatBeltType, PretensionerId, Pretensioner, AirBagLocFrontId, AirBagLocFront, AirBagLocKneeId, AirBagLocKnee, AirBagLocSideId, AirBagLocSide, AirBagLocCurtainId, AirBagLocCurtain, AirBagLocSeatCushionId, AirBagLocSeatCushion, OtherRestraintSystemInfo, ForwardCollisionWarningId, ForwardCollisionWarning, DynamicBrakeSupportId, DynamicBrakeSupport, CrashImminentBrakingID, CrashImminentBraking, PedestrianAutoEmergencyBrakingId, PedestrianAutoEmergencyBraking, BlindSpotWarningId, BlindSpotWarning, BlindSpotInterventionId, BlindSpotIntervention, LaneDepartureWarningId, LaneDepartureWarning, LaneKeepingAssistanceId, LaneKeepingAssistance, LaneCenteringAssistanceId, LaneCenteringAssistance, BackupCameraId, BackupCamera, RearCrossTrafficAlertId, RearCrossTrafficAlert, RearAutomaticEmergencyBrakingId, RearAutomaticEmergencyBraking, ParkAssistId, ParkAssist, DaytimeRunningLightId, DaytimeRunningLight, HeadlampLightSourceId, HeadlampLightSource, SemiAutoHeadlampBeamSwitchingId, SemiAutoHeadlampBeamSwitching, AdaptiveDrivingBeamId, AdaptiveDrivingBeam, AdaptiveCruiseControlId, AdaptiveCruiseControl, AntilockBrakeSystemId, AntilockBrakeSystem, ElectronicStabilityControlId, ElectronicStabilityControl, TPMSId, TPMS, AutomaticCrashNotificationId, AutomaticCrashNotification, EventDataRecorderId, EventDataRecorder, TractionControlId, TractionControl, AutoPedestrianAlertingSoundId, AutoPedestrianAlertingSound, KeylessIgnitionId, KeylessIgnition, SAEAutomationLevel_From, SAEAutomationLevel_to, AutoReverseSystemId, AutoReverseSystem, ActiveSafetySysNote, POLKVIN
```

| Year | Added columns | Removed columns | Shared column order changed? |
|---|---|---|---|
| 2021 | None | None | No |
| 2022 | `NonLandUseId`, `NonLandUse` | `POLKVIN` | No |
| 2023 | `VEHICLEDESCRIPTOR`, `VINDECODEDON`, `VINDECODEERROR`, `VEHICLETYPEID`, `VEHICLETYPE`, `MANUFACTURERFULLNAMEID`, `MANUFACTURERFULLNAME`, `MAKEID`, `MAKE`, `MODELID`, `MODEL`, `MODELYEAR`, `SERIES`, `TRIM`, `SERIES2`, `TRIM2`, `PLANTCOUNTRYID`, `PLANTCOUNTRY`, `PLANTSTATE`, `PLANTCITY`, `PLANTCOMPANYNAME`, `DESTINATIONMARKETID`, `DESTINATIONMARKET`, `BASEPRICE`, `NONLANDUSEID`, `NONLANDUSE`, `NOTE`, `BODYCLASSID`, `BODYCLASS`, `DOORSCOUNT`, `WINDOWS`, `WHEELBASETYPEID`, `WHEELBASETYPE`, `TRACKWIDTHIN`, `GROSSVEHICLEWEIGHTRATINGFROMID`, `GROSSVEHICLEWEIGHTRATINGFROM`, `GROSSVEHICLEWEIGHTRATINGTOID`, `GROSSVEHICLEWEIGHTRATINGTO`, `GROSSCOMBWEIGHTRATINGFROMID`, `GROSSCOMBWEIGHTRATINGFROM`, `GROSSCOMBWEIGHTRATINGTOID`, `GROSSCOMBWEIGHTRATINGTO`, `CURBWEIGHTLB`, `WHEELBASEIN_FROM`, `WHEELBASEIN_TO`, `WHEELSCOUNT`, `WHEELSIZEFRONTIN`, `WHEELSIZEREARIN`, `TRUCKBODYCABTYPEID`, `TRUCKBODYCABTYPE`, `TRUCKBEDTYPEID`, `TRUCKBEDTYPE`, `TRUCKBEDLENGTHIN`, `BUSTYPEID`, `BUSTYPE`, `BUSFLOORCONFIGURATIONTYPEID`, `BUSFLOORCONFIGURATIONTYPE`, `BUSLENGTHFT`, `OTHERBUSINFO`, `CUSTOMMOTORCYCLETYPEID`, `CUSTOMMOTORCYCLETYPE`, `MOTORCYCLESUSPENSIONTYPEID`, `MOTORCYCLESUSPENSIONTYPE`, `MOTORCYCLECHASSISTYPEID`, `MOTORCYCLECHASSISTYPE`, `OTHERMOTORCYCLEINFO`, `STEERINGLOCATIONID`, `STEERINGLOCATION`, `ENTERTAINMENTSYSTEMID`, `ENTERTAINMENTSYSTEM`, `SEATSCOUNT`, `SEATROWSCOUNT`, `TRANSMISSIONSPEEDS`, `TRANSMISSIONSTYLEID`, `TRANSMISSIONSTYLE`, `DRIVETYPEID`, `DRIVETYPE`, `AXLESCOUNT`, `AXLECONFIGURATIONID`, `AXLECONFIGURATION`, `BRAKESYSTEMTYPEID`, `BRAKESYSTEMTYPE`, `BRAKESYSTEMDESC`, `EVDRIVEUNITID`, `EVDRIVEUNIT`, `BATTERYKWH_FROM`, `BATTERYKWH_TO`, `BATTERYV_FROM`, `BATTERYV_TO`, `BATTERYA_FROM`, `BATTERYA_TO`, `BATTERYPACKSPERVEHICLE`, `BATTERYMODULESPERPACK`, `BATTERYCELLSPERMODULE`, `BATTERYTYPEID`, `BATTERYTYPE`, `OTHERBATTERYINFO`, `CHARGERLEVELID`, `CHARGERLEVEL`, `CHARGERPOWERKW`, `ENGINEMANUFACTURER`, `ENGINEMODEL`, `ENGINECONFIGURATIONID`, `ENGINECONFIGURATION`, `ENGINEPOWERKW`, `ENGINESTROKECYCLES`, `ENGINECYLINDERSCOUNT`, `ENGINEBRAKEHP_FROM`, `ENGINEBRAKEHP_TO`, `ENGINECOOLINGTYPEID`, `ENGINECOOLINGTYPE`, `DISPLACEMENTCI`, `DISPLACEMENTCC`, `DISPLACEMENTL`, `FUELTYPEPRIMARYID`, `FUELTYPEPRIMARY`, `FUELTYPESECONDARYID`, `FUELTYPESECONDARY`, `FUELDELIVERYINJECTIONTYPEID`, `FUELDELIVERYINJECTIONTYPE`, `ENGINEVALVETRAINDESIGNID`, `ENGINEVALVETRAINDESIGN`, `ENGINEELECTRIFICATIONLEVELID`, `ENGINEELECTRIFICATIONLEVEL`, `ENGINETURBOID`, `ENGINETURBO`, `TOPSPEEDMPH`, `OTHERENGINEINFO`, `SEATBELTTYPEID`, `SEATBELTTYPE`, `PRETENSIONERID`, `PRETENSIONER`, `AIRBAGLOCFRONTID`, `AIRBAGLOCFRONT`, `AIRBAGLOCKNEEID`, `AIRBAGLOCKNEE`, `AIRBAGLOCSIDEID`, `AIRBAGLOCSIDE`, `AIRBAGLOCCURTAINID`, `AIRBAGLOCCURTAIN`, `AIRBAGLOCSEATCUSHIONID`, `AIRBAGLOCSEATCUSHION`, `OTHERRESTRAINTSYSTEMINFO`, `FORWARDCOLLISIONWARNINGID`, `FORWARDCOLLISIONWARNING`, `DYNAMICBRAKESUPPORTID`, `DYNAMICBRAKESUPPORT`, `CRASHIMMINENTBRAKINGID`, `CRASHIMMINENTBRAKING`, `PEDESTRIANAUTOEMERGENCYBRAKINGID`, `PEDESTRIANAUTOEMERGENCYBRAKING`, `BLINDSPOTWARNINGID`, `BLINDSPOTWARNING`, `BLINDSPOTINTERVENTIONID`, `BLINDSPOTINTERVENTION`, `LANEDEPARTUREWARNINGID`, `LANEDEPARTUREWARNING`, `LANEKEEPINGASSISTANCEID`, `LANEKEEPINGASSISTANCE`, `LANECENTERINGASSISTANCEID`, `LANECENTERINGASSISTANCE`, `BACKUPCAMERAID`, `BACKUPCAMERA`, `REARCROSSTRAFFICALERTID`, `REARCROSSTRAFFICALERT`, `REARAUTOMATICEMERGENCYBRAKINGID`, `REARAUTOMATICEMERGENCYBRAKING`, `PARKASSISTID`, `PARKASSIST`, `DAYTIMERUNNINGLIGHTID`, `DAYTIMERUNNINGLIGHT`, `HEADLAMPLIGHTSOURCEID`, `HEADLAMPLIGHTSOURCE`, `SEMIAUTOHEADLAMPBEAMSWITCHINGID`, `SEMIAUTOHEADLAMPBEAMSWITCHING`, `ADAPTIVEDRIVINGBEAMID`, `ADAPTIVEDRIVINGBEAM`, `ADAPTIVECRUISECONTROLID`, `ADAPTIVECRUISECONTROL`, `ANTILOCKBRAKESYSTEMID`, `ANTILOCKBRAKESYSTEM`, `ELECTRONICSTABILITYCONTROLID`, `ELECTRONICSTABILITYCONTROL`, `TPMSID`, `AUTOMATICCRASHNOTIFICATIONID`, `AUTOMATICCRASHNOTIFICATION`, `EVENTDATARECORDERID`, `EVENTDATARECORDER`, `TRACTIONCONTROLID`, `TRACTIONCONTROL`, `AUTOPEDESTRIANALERTINGSOUNDID`, `AUTOPEDESTRIANALERTINGSOUND`, `KEYLESSIGNITIONID`, `KEYLESSIGNITION`, `SAEAUTOMATIONLEVEL_FROM`, `SAEAUTOMATIONLEVEL_TO`, `AUTOREVERSESYSTEMID`, `AUTOREVERSESYSTEM`, `ACTIVESAFETYSYSNOTE` | `VehicleDescriptor`, `VINDecodedOn`, `VINDecodeError`, `VehicleTypeId`, `VehicleType`, `ManufacturerFullNameId`, `ManufacturerFullName`, `MakeId`, `Make`, `ModelId`, `Model`, `ModelYear`, `Series`, `Trim`, `Series2`, `Trim2`, `PlantCountryId`, `PlantCountry`, `PlantState`, `PlantCity`, `PlantCompanyName`, `DestinationMarketId`, `DestinationMarket`, `BasePrice`, `NonLandUseId`, `NonLandUse`, `Note`, `BodyClassId`, `BodyClass`, `DoorsCount`, `Windows`, `WheelBaseTypeId`, `WheelBaseType`, `TrackWidthIN`, `GrossVehicleWeightRatingFromId`, `GrossVehicleWeightRatingFrom`, `GrossVehicleWeightRatingToId`, `GrossVehicleWeightRatingTo`, `GrossCombWeightRatingFromId`, `GrossCombWeightRatingFrom`, `GrossCombWeightRatingToId`, `GrossCombWeightRatingTo`, `CurbWeightLB`, `WheelBaseIN_from`, `WheelBaseIN_To`, `WheelsCount`, `WheelSizeFrontIN`, `WheelSizeRearIN`, `TruckBodyCabTypeId`, `TruckBodyCabType`, `TruckBedTypeId`, `TruckBedType`, `TruckBedLengthIN`, `BusTypeId`, `BusType`, `BusFloorConfigurationTypeId`, `BusFloorConfigurationType`, `BusLengthFT`, `OtherBusInfo`, `CustomMotorcycleTypeId`, `CustomMotorcycleType`, `MotorcycleSuspensionTypeId`, `MotorcycleSuspensionType`, `MotorcycleChassisTypeId`, `MotorcycleChassisType`, `OtherMotorcycleInfo`, `SteeringLocationId`, `SteeringLocation`, `EntertainmentSystemId`, `EntertainmentSystem`, `SeatsCount`, `SeatRowsCount`, `TransmissionSpeeds`, `TransmissionStyleId`, `TransmissionStyle`, `DriveTypeId`, `DriveType`, `AxlesCount`, `AxleConfigurationId`, `AxleConfiguration`, `BrakeSystemTypeId`, `BrakeSystemType`, `BrakeSystemDesc`, `EVDriveUnitId`, `EVDriveUnit`, `BatteryKWh_From`, `BatteryKWh_to`, `BatteryV_From`, `BatteryV_to`, `BatteryA_From`, `BatteryA_to`, `BatteryPacksPerVehicle`, `BatteryModulesPerPack`, `BatteryCellsPerModule`, `BatteryTypeId`, `BatteryType`, `OtherBatteryInfo`, `ChargerLevelId`, `ChargerLevel`, `ChargerPowerKW`, `EngineManufacturer`, `EngineModel`, `EngineConfigurationId`, `EngineConfiguration`, `EnginePowerKW`, `EngineStrokeCycles`, `EngineCylindersCount`, `EngineBrakeHP_From`, `EngineBrakeHP_To`, `EngineCoolingTypeId`, `EngineCoolingType`, `DisplacementCI`, `DisplacementCC`, `DisplacementL`, `FuelTypePrimaryId`, `FuelTypePrimary`, `FuelTypeSecondaryId`, `FuelTypeSecondary`, `FuelDeliveryInjectionTypeId`, `FuelDeliveryInjectionType`, `EngineValveTrainDesignId`, `EngineValveTrainDesign`, `EngineElectrificationLevelId`, `EngineElectrificationLevel`, `EngineTurboId`, `EngineTurbo`, `TopSpeedMPH`, `OtherEngineInfo`, `SeatBeltTypeId`, `SeatBeltType`, `PretensionerId`, `Pretensioner`, `AirBagLocFrontId`, `AirBagLocFront`, `AirBagLocKneeId`, `AirBagLocKnee`, `AirBagLocSideId`, `AirBagLocSide`, `AirBagLocCurtainId`, `AirBagLocCurtain`, `AirBagLocSeatCushionId`, `AirBagLocSeatCushion`, `OtherRestraintSystemInfo`, `ForwardCollisionWarningId`, `ForwardCollisionWarning`, `DynamicBrakeSupportId`, `DynamicBrakeSupport`, `CrashImminentBrakingID`, `CrashImminentBraking`, `PedestrianAutoEmergencyBrakingId`, `PedestrianAutoEmergencyBraking`, `BlindSpotWarningId`, `BlindSpotWarning`, `BlindSpotInterventionId`, `BlindSpotIntervention`, `LaneDepartureWarningId`, `LaneDepartureWarning`, `LaneKeepingAssistanceId`, `LaneKeepingAssistance`, `LaneCenteringAssistanceId`, `LaneCenteringAssistance`, `BackupCameraId`, `BackupCamera`, `RearCrossTrafficAlertId`, `RearCrossTrafficAlert`, `RearAutomaticEmergencyBrakingId`, `RearAutomaticEmergencyBraking`, `ParkAssistId`, `ParkAssist`, `DaytimeRunningLightId`, `DaytimeRunningLight`, `HeadlampLightSourceId`, `HeadlampLightSource`, `SemiAutoHeadlampBeamSwitchingId`, `SemiAutoHeadlampBeamSwitching`, `AdaptiveDrivingBeamId`, `AdaptiveDrivingBeam`, `AdaptiveCruiseControlId`, `AdaptiveCruiseControl`, `AntilockBrakeSystemId`, `AntilockBrakeSystem`, `ElectronicStabilityControlId`, `ElectronicStabilityControl`, `TPMSId`, `AutomaticCrashNotificationId`, `AutomaticCrashNotification`, `EventDataRecorderId`, `EventDataRecorder`, `TractionControlId`, `TractionControl`, `AutoPedestrianAlertingSoundId`, `AutoPedestrianAlertingSound`, `KeylessIgnitionId`, `KeylessIgnition`, `SAEAutomationLevel_From`, `SAEAutomationLevel_to`, `AutoReverseSystemId`, `AutoReverseSystem`, `ActiveSafetySysNote` | No |
| 2024 | None | None | No |

## vpictrailerdecode.csv

2020 columns:

```text
CASENUM, VEH_NO, TRAILER_NO, VehicleDescriptor, VINDecodedOn, VINDecodeError, VehicleTypeId, VehicleType, ManufacturerFullNameId, ManufacturerFullName, MakeId, Make, ModelId, Model, ModelYear, Series, Trim, PlantCountryId, PlantCountry, PlantState, PlantCity, PlantCompanyName, Note, BodyClassId, BodyClass, GrossVehicleWeightRatingFromId, GrossVehicleWeightRatingFrom, GrossVehicleWeightRatingToId, GrossVehicleWeightRatingTo, TrailerBodyTypeId, TrailerBodyType, TrailerTypeConnectionId, TrailerTypeConnection, TrailerLengthFT, OtherTrailerInfo, AxlesCount, AxleConfigurationId, AxleConfiguration
```

| Year | Added columns | Removed columns | Shared column order changed? |
|---|---|---|---|
| 2021 | None | None | No |
| 2022 | `VEHICLEDESCRIPTOR`, `VINDECODEDON`, `VINDECODEERROR`, `VEHICLETYPEID`, `VEHICLETYPE`, `MANUFACTURERFULLNAMEID`, `MANUFACTURERFULLNAME`, `MAKEID`, `MAKE`, `MODELID`, `MODEL`, `MODELYEAR`, `SERIES`, `TRIM`, `PLANTCOUNTRYID`, `PLANTCOUNTRY`, `PLANTSTATE`, `PLANTCITY`, `PLANTCOMPANYNAME`, `NONLANDUSEID`, `NONLANDUSE`, `NOTE`, `BODYCLASSID`, `BODYCLASS`, `GROSSVEHICLEWEIGHTRATINGFROMID`, `GROSSVEHICLEWEIGHTRATINGFROM`, `GROSSVEHICLEWEIGHTRATINGTOID`, `GROSSVEHICLEWEIGHTRATINGTO`, `TRAILERBODYTYPEID`, `TRAILERBODYTYPE`, `TRAILERTYPECONNECTIONID`, `TRAILERTYPECONNECTION`, `TRAILERLENGTHFT`, `OTHERTRAILERINFO`, `AXLESCOUNT`, `AXLECONFIGURATIONID`, `AXLECONFIGURATION` | `VehicleDescriptor`, `VINDecodedOn`, `VINDecodeError`, `VehicleTypeId`, `VehicleType`, `ManufacturerFullNameId`, `ManufacturerFullName`, `MakeId`, `Make`, `ModelId`, `Model`, `ModelYear`, `Series`, `Trim`, `PlantCountryId`, `PlantCountry`, `PlantState`, `PlantCity`, `PlantCompanyName`, `Note`, `BodyClassId`, `BodyClass`, `GrossVehicleWeightRatingFromId`, `GrossVehicleWeightRatingFrom`, `GrossVehicleWeightRatingToId`, `GrossVehicleWeightRatingTo`, `TrailerBodyTypeId`, `TrailerBodyType`, `TrailerTypeConnectionId`, `TrailerTypeConnection`, `TrailerLengthFT`, `OtherTrailerInfo`, `AxlesCount`, `AxleConfigurationId`, `AxleConfiguration` | No |
| 2023 | None | None | No |
| 2024 | None | None | No |

## vsoe.csv

2020 columns:

```text
CASENUM, VEH_NO, STRATUM, STRATUMNAME, REGION, REGIONNAME, PSU, PJ, PSU_VAR, URBANICITY, URBANICITYNAME, VEVENTNUM, SOE, SOENAME, AOI, AOINAME, PSUSTRAT, WEIGHT
```

| Year | Added columns | Removed columns | Shared column order changed? |
|---|---|---|---|
| 2021 | None | None | No |
| 2022 | None | None | No |
| 2023 | None | None | Yes |
| 2024 | None | None | No |

## weather.csv

2020 columns:

```text
CASENUM, STRATUM, STRATUMNAME, REGION, REGIONNAME, PSU, PJ, PSU_VAR, URBANICITY, URBANICITYNAME, WEATHERCode, WEATHERNAME, PSUSTRAT, WEIGHT
```

| Year | Added columns | Removed columns | Shared column order changed? |
|---|---|---|---|
| 2021 | `WEATHER` | `WEATHERCode` | No |
| 2022 | None | None | No |
| 2023 | None | None | Yes |
| 2024 | None | None | No |

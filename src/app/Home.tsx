import {
    Box,
    Button,
    Chip,
    MenuItem,
    Paper,
    Select,
    Stack,
    TextField,
    ToggleButton,
    ToggleButtonGroup,
    Typography,
} from "@mui/material";
import { motion } from "motion/react";
import { BatteryFull, ChartNoAxesCombined, Clock3 } from "lucide-react";
import { useMemo, useState } from "react";
import type { AppLanguage } from "@/Entry";

const MotionBox = motion.create(Box);

type ForkliftType = "CB" | "WH";

type ModelDefinition = {
    code: string;
    type: ForkliftType;
    useAhPerHour: number;
};

const models: ModelDefinition[] = [
    { code: "8FBE15", type: "CB", useAhPerHour: 79 },
    { code: "8FBN20", type: "CB", useAhPerHour: 102 },
    { code: "8FB20", type: "CB", useAhPerHour: 67 },
    { code: "8FBR15", type: "WH", useAhPerHour: 56 },
    { code: "8FBR20", type: "WH", useAhPerHour: 66 },
    { code: "8FBP25", type: "WH", useAhPerHour: 73 },
];

const batteryOptions = [302, 456, 604];

const modeMultiplier = {
    Economy: 0.82,
    Standard: 1,
    Power: 1.15,
    "High Power": 1.28,
} as const;

const containerVariants = {
    hidden: { opacity: 0 },
    show: {
        opacity: 1,
        transition: { staggerChildren: 0.1 },
    },
};

const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { duration: 0.3 } },
};

interface HomeProps {
    language: AppLanguage;
}

export default function Home({ language }: HomeProps) {
    const [forkliftType, setForkliftType] = useState<ForkliftType>("CB");
    const [model, setModel] = useState<string>("8FBE15");
    const [batteryAh, setBatteryAh] = useState<number>(456);
    const [operationMode, setOperationMode] =
        useState<keyof typeof modeMultiplier>("Standard");
    const [hoursPerShift, setHoursPerShift] = useState<number>(8);
    const [shiftCount, setShiftCount] = useState<number>(2);
    const [breakMinutes, setBreakMinutes] = useState<number>(75);
    const [chargeMinutes, setChargeMinutes] = useState<number>(30);
    const [chargerAmp, setChargerAmp] = useState<number>(200);

    const t = useMemo(
        () =>
            language === "id"
                ? {
                      setup: "Pengaturan Simulator",
                      intro: "Masukkan data utama untuk estimasi cepat.",
                      type: "Tipe forklift",
                      model: "Model",
                      battery: "Kapasitas baterai (Ah)",
                      mode: "Mode operasi",
                      shifts: "Jumlah shift",
                      hours: "Jam per shift",
                      break: "Total istirahat per hari (menit)",
                      charge: "Peluang charging per hari (menit)",
                      charger: "Arus charger (A)",
                      reset: "Reset cepat",
                      estimate: "Hasil Estimasi",
                      available: "Energi tersedia",
                      needed: "Energi dibutuhkan",
                      runtime: "Perkiraan runtime",
                      safe: "Aman untuk jadwal saat ini",
                      risky: "Perlu charging tambahan atau baterai lebih besar",
                      cb: "Counterbalance",
                      wh: "Warehouse",
                      stats: "ringkas",
                      schedule: "jadwal",
                      idle: "jam idle",
                  }
                : {
                      setup: "Simulator Setup",
                      intro: "Enter key inputs for a quick planning estimate.",
                      type: "Forklift type",
                      model: "Model",
                      battery: "Battery capacity (Ah)",
                      mode: "Operation mode",
                      shifts: "Shift count",
                      hours: "Hours per shift",
                      break: "Total breaks per day (minutes)",
                      charge: "Charging opportunity per day (minutes)",
                      charger: "Charger current (A)",
                      reset: "Quick reset",
                      estimate: "Estimated Result",
                      available: "Available energy",
                      needed: "Required energy",
                      runtime: "Estimated runtime",
                      safe: "Safe for current schedule",
                      risky: "Needs extra charging or larger battery",
                      cb: "Counterbalance",
                      wh: "Warehouse",
                      stats: "overview",
                      schedule: "schedule",
                      idle: "idle hours",
                  },
        [language],
    );

    const typeModels = useMemo(
        () => models.filter((entry) => entry.type === forkliftType),
        [forkliftType],
    );

    const selectedModel =
        models.find((entry) => entry.code === model) ?? typeModels[0];

    const calculation = useMemo(() => {
        const useRate = selectedModel.useAhPerHour * modeMultiplier[operationMode];
        const totalWorkHours = Math.max(hoursPerShift * shiftCount, 0);
        const chargeRecoveredAh = (chargeMinutes / 60) * chargerAmp * 0.85;
        const usableAh = batteryAh * 0.95 + chargeRecoveredAh;
        const requiredAh = totalWorkHours * useRate;
        const estimatedRuntimeHours = useRate > 0 ? usableAh / useRate : 0;

        return {
            useRate,
            totalWorkHours,
            usableAh,
            requiredAh,
            estimatedRuntimeHours,
            isSafe: estimatedRuntimeHours >= totalWorkHours,
            idleHours: breakMinutes / 60,
        };
    }, [
        selectedModel,
        operationMode,
        hoursPerShift,
        shiftCount,
        chargeMinutes,
        chargerAmp,
        batteryAh,
        breakMinutes,
    ]);

    const resetToDefault = () => {
        setForkliftType("CB");
        setModel("8FBE15");
        setBatteryAh(456);
        setOperationMode("Standard");
        setHoursPerShift(8);
        setShiftCount(2);
        setBreakMinutes(75);
        setChargeMinutes(30);
        setChargerAmp(200);
    };

    return (
        <Box sx={{ py: 2 }}>
            <MotionBox
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                sx={{ mb: 3, maxWidth: 720 }}
            >
                <Typography
                    variant="h5"
                    sx={{
                        fontWeight: 850,
                        mb: 1,
                        letterSpacing: "-0.03em",
                    }}
                >
                    {t.setup}
                </Typography>
                <Typography
                    variant="body1"
                    sx={{
                        color: "text.secondary",
                        lineHeight: 1.65,
                    }}
                >
                    {t.intro}
                </Typography>
            </MotionBox>

            <MotionBox
                variants={containerVariants}
                initial="hidden"
                animate="show"
                sx={{
                    display: "grid",
                    gridTemplateColumns: {
                        xs: "1fr",
                        md: "1.2fr 1fr",
                    },
                    gap: 2,
                }}
            >
                <MotionBox variants={itemVariants}>
                    <Paper
                        sx={{
                            p: 2.2,
                            borderRadius: 4,
                            border: "1px solid",
                            borderColor: "divider",
                            background:
                                "linear-gradient(160deg, rgba(255,255,255,0.84), rgba(240,247,251,0.86))",
                        }}
                    >
                        <Stack spacing={2}>
                            <Box>
                                <Typography variant="overline" sx={{ opacity: 0.8 }}>
                                    {t.stats}
                                </Typography>
                                <Typography variant="h6" sx={{ fontWeight: 850 }}>
                                    {selectedModel.code}
                                </Typography>
                            </Box>

                            <Stack direction={{ xs: "column", sm: "row" }} spacing={1.1}>
                                <Chip
                                    icon={<BatteryFull size={16} />}
                                    label={`${t.available}: ${calculation.usableAh.toFixed(0)} Ah`}
                                    color="success"
                                    variant="outlined"
                                />
                                <Chip
                                    icon={<ChartNoAxesCombined size={16} />}
                                    label={`${t.needed}: ${calculation.requiredAh.toFixed(0)} Ah`}
                                    color="primary"
                                    variant="outlined"
                                />
                            </Stack>

                            <Typography
                                sx={{ fontSize: { xs: 30, sm: 36 }, fontWeight: 900 }}
                            >
                                {calculation.estimatedRuntimeHours.toFixed(1)}h
                            </Typography>
                            <Typography sx={{ color: "text.secondary" }}>
                                {t.runtime}
                            </Typography>

                            <Typography
                                sx={{
                                    color: calculation.isSafe
                                        ? "success.dark"
                                        : "warning.dark",
                                    fontWeight: 700,
                                }}
                            >
                                {calculation.isSafe ? t.safe : t.risky}
                            </Typography>
                        </Stack>
                    </Paper>
                </MotionBox>

                <MotionBox variants={itemVariants}>
                    <Paper
                        sx={{
                            p: 2.2,
                            borderRadius: 4,
                            border: "1px solid",
                            borderColor: "divider",
                        }}
                    >
                        <Stack spacing={1.5}>
                            <Typography variant="subtitle2" color="text.secondary">
                                {t.type}
                            </Typography>
                            <ToggleButtonGroup
                                value={forkliftType}
                                exclusive
                                fullWidth
                                onChange={(_, value: ForkliftType | null) => {
                                    if (!value) return;
                                    setForkliftType(value);
                                    const firstModel = models.find(
                                        (item) => item.type === value,
                                    );
                                    if (firstModel) setModel(firstModel.code);
                                }}
                            >
                                <ToggleButton value="CB">{t.cb}</ToggleButton>
                                <ToggleButton value="WH">{t.wh}</ToggleButton>
                            </ToggleButtonGroup>

                            <Typography variant="subtitle2" color="text.secondary">
                                {t.model}
                            </Typography>
                            <Select
                                fullWidth
                                size="small"
                                value={model}
                                onChange={(event) => setModel(event.target.value)}
                            >
                                {typeModels.map((entry) => (
                                    <MenuItem key={entry.code} value={entry.code}>
                                        {entry.code}
                                    </MenuItem>
                                ))}
                            </Select>

                            <Typography variant="subtitle2" color="text.secondary">
                                {t.battery}
                            </Typography>
                            <ToggleButtonGroup
                                value={batteryAh}
                                exclusive
                                fullWidth
                                onChange={(_, value: number | null) => {
                                    if (value) setBatteryAh(value);
                                }}
                            >
                                {batteryOptions.map((option) => (
                                    <ToggleButton key={option} value={option}>
                                        {option}
                                    </ToggleButton>
                                ))}
                            </ToggleButtonGroup>

                            <Typography variant="subtitle2" color="text.secondary">
                                {t.mode}
                            </Typography>
                            <Select
                                fullWidth
                                size="small"
                                value={operationMode}
                                onChange={(event) =>
                                    setOperationMode(
                                        event.target
                                            .value as keyof typeof modeMultiplier,
                                    )
                                }
                            >
                                {Object.keys(modeMultiplier).map((entry) => (
                                    <MenuItem key={entry} value={entry}>
                                        {entry}
                                    </MenuItem>
                                ))}
                            </Select>

                            <Typography variant="subtitle2" color="text.secondary">
                                {t.schedule}
                            </Typography>
                            <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
                                <TextField
                                    label={t.shifts}
                                    type="number"
                                    size="small"
                                    value={shiftCount}
                                    onChange={(event) =>
                                        setShiftCount(Number(event.target.value))
                                    }
                                    slotProps={{ htmlInput: { min: 1, max: 4 } }}
                                />
                                <TextField
                                    label={t.hours}
                                    type="number"
                                    size="small"
                                    value={hoursPerShift}
                                    onChange={(event) =>
                                        setHoursPerShift(Number(event.target.value))
                                    }
                                    slotProps={{ htmlInput: { min: 1, max: 12 } }}
                                />
                            </Stack>

                            <TextField
                                label={t.break}
                                type="number"
                                size="small"
                                value={breakMinutes}
                                onChange={(event) =>
                                    setBreakMinutes(Number(event.target.value))
                                }
                                slotProps={{ htmlInput: { min: 0, max: 300 } }}
                            />

                            <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
                                <TextField
                                    fullWidth
                                    label={t.charge}
                                    type="number"
                                    size="small"
                                    value={chargeMinutes}
                                    onChange={(event) =>
                                        setChargeMinutes(Number(event.target.value))
                                    }
                                    slotProps={{ htmlInput: { min: 0, max: 240 } }}
                                />
                                <TextField
                                    fullWidth
                                    label={t.charger}
                                    type="number"
                                    size="small"
                                    value={chargerAmp}
                                    onChange={(event) =>
                                        setChargerAmp(Number(event.target.value))
                                    }
                                    slotProps={{ htmlInput: { min: 50, max: 500 } }}
                                />
                            </Stack>

                            <Box
                                sx={{
                                    display: "flex",
                                    justifyContent: "space-between",
                                    alignItems: "center",
                                    gap: 1,
                                }}
                            >
                                <Chip
                                    icon={<Clock3 size={15} />}
                                    label={`${calculation.idleHours.toFixed(1)} ${t.idle}`}
                                />
                                <Button
                                    variant="outlined"
                                    color="inherit"
                                    onClick={resetToDefault}
                                >
                                    {t.reset}
                                </Button>
                            </Box>
                        </Stack>
                    </Paper>
                </MotionBox>
            </MotionBox>

            <MotionBox
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3, duration: 0.4 }}
                sx={{ mt: 2 }}
            >
                <Paper
                    sx={{
                        p: 2,
                        borderRadius: 4,
                        border: "1px dashed",
                        borderColor: "divider",
                        bgcolor: "background.paper",
                    }}
                >
                    <Typography variant="subtitle1" sx={{ fontWeight: 800 }}>
                        {t.estimate}
                    </Typography>
                    <Typography color="text.secondary" sx={{ mt: 0.5 }}>
                        {selectedModel.code} · {calculation.useRate.toFixed(1)} Ah/h ·{" "}
                        {calculation.totalWorkHours.toFixed(1)}h working hours.
                    </Typography>
                </Paper>
            </MotionBox>
        </Box>
    );
}

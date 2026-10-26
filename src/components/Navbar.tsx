import { ReactNode, useEffect, useState } from "react";
import logo from "../logo.png";
import {
    Box,
    Button,
    Container,
    IconButton,
    ToggleButton,
    ToggleButtonGroup,
    Typography,
} from "@mui/material";
import { useColorScheme } from "@mui/material/styles";
import { Moon, Sun } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import type { AppLanguage } from "@/Entry";

interface BeforeInstallPromptEvent extends Event {
    readonly platforms: string[];
    readonly userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
    prompt: () => Promise<void>;
}

export interface NavbarProps {
    children?: ReactNode;
    language: AppLanguage;
    onLanguageChange: (language: AppLanguage) => void;
}

export default function Navbar({
    children,
    language,
    onLanguageChange,
}: NavbarProps) {
    const { mode, systemMode, setMode } = useColorScheme();
    const [mounted, setMounted] = useState(false);
    const [installPrompt, setInstallPrompt] =
        useState<BeforeInstallPromptEvent | null>(null);
    const [isInstalled, setIsInstalled] = useState(false);

    useEffect(() => {
        setMounted(true);

        const mediaQuery = window.matchMedia("(display-mode: standalone)");
        const detectInstalled = () => {
            const standaloneMode = mediaQuery.matches;
            const iosStandalone = Boolean((window.navigator as any).standalone);
            setIsInstalled(standaloneMode || iosStandalone);
        };

        const onBeforeInstallPrompt = (event: Event) => {
            event.preventDefault();
            setInstallPrompt(event as BeforeInstallPromptEvent);
        };

        const onInstalled = () => {
            setIsInstalled(true);
            setInstallPrompt(null);
        };

        detectInstalled();

        window.addEventListener("beforeinstallprompt", onBeforeInstallPrompt);
        window.addEventListener("appinstalled", onInstalled);
        mediaQuery.addEventListener("change", detectInstalled);
        return () => {
            window.removeEventListener(
                "beforeinstallprompt",
                onBeforeInstallPrompt,
            );
            window.removeEventListener("appinstalled", onInstalled);
            mediaQuery.removeEventListener("change", detectInstalled);
        };
    }, []);

    const isDark = mode === "system" ? systemMode === "dark" : mode === "dark";

    const toggleThemeColor = () => {
        setMode(isDark ? "light" : "dark");
    };

    const askInstall = async () => {
        if (!installPrompt) return;
        await installPrompt.prompt();
        await installPrompt.userChoice;
        setInstallPrompt(null);
    };

    const askUninstall = async () => {
        const copy = {
            en: {
                confirm:
                    "Remove local app data and show uninstall steps? The app icon still needs to be removed from your browser or device manually.",
                done: "App data has been cleared. To uninstall fully, remove this app from your browser or device installed apps list.",
            },
            id: {
                confirm:
                    "Hapus data lokal aplikasi dan tampilkan langkah uninstall? Ikon aplikasi tetap perlu dihapus manual dari browser atau perangkat.",
                done: "Data aplikasi sudah dibersihkan. Untuk uninstall penuh, hapus aplikasi ini dari daftar aplikasi terpasang di browser/perangkat Anda.",
            },
        };

        const accepted = window.confirm(copy[language].confirm);
        if (!accepted) return;

        try {
            if ("serviceWorker" in navigator) {
                const registrations = await navigator.serviceWorker.getRegistrations();
                await Promise.all(
                    registrations.map((registration) => registration.unregister()),
                );
            }

            if ("caches" in window) {
                const cacheKeys = await caches.keys();
                await Promise.all(cacheKeys.map((key) => caches.delete(key)));
            }

            localStorage.removeItem("traknus-lang");
            localStorage.removeItem("theme-mode");
        } finally {
            setIsInstalled(false);
            alert(copy[language].done);
        }
    };

    const copy = {
        en: {
            install: "Install",
            uninstall: "Uninstall",
            theme: "Toggle color theme",
        },
        id: {
            install: "Pasang",
            uninstall: "Uninstall",
            theme: "Ubah tema warna",
        },
    };

    const canInstall = Boolean(installPrompt);
    const actionLabel = isInstalled ? copy[language].uninstall : copy[language].install;
    const actionEnabled = isInstalled || canInstall;
    const actionHandler = isInstalled ? askUninstall : askInstall;

    return (
        <Box
            component="header"
            sx={{
                position: "sticky",
                top: 0,
                zIndex: 1200,
                backdropFilter: "blur(16px)",
                backgroundColor:
                    "rgba(var(--template-palette-background-paperChannel, 255, 255, 255) / 0.74)",
                borderBottom: "1px solid",
                borderColor: "divider",
                py: 1.2,
            }}
        >
            <Container>
                <Box
                    component={motion.div}
                    initial={{ y: -70, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ type: "spring", stiffness: 120, damping: 20 }}
                    sx={{
                        display: "flex",
                        flexDirection: "row",
                        justifyContent: "space-between",
                        alignItems: "center",
                    }}
                >
                    <Box
                        sx={{
                            display: "flex",
                            alignItems: "center",
                            gap: 1.5,
                        }}
                    >
                            <Box
                                component={motion.div}
                                whileHover={{ scale: 1.04 }}
                            >
                                <Box
                                    component="img"
                                    sx={{
                                        width: { xs: "122px", sm: "158px" },
                                        height: { xs: "40px", sm: "52px" },
                                        objectFit: "contain",
                                    }}
                                    src={logo}
                                    alt="Traknus"
                                />
                            </Box>
                        <Typography
                            variant="subtitle2"
                            sx={{
                                display: { xs: "none", md: "block" },
                                color: "text.secondary",
                                letterSpacing: ".06em",
                                fontWeight: 800,
                                textTransform: "uppercase",
                            }}
                        >
                            Battery Tool
                        </Typography>
                    </Box>

                    <Box
                        component={motion.div}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.2, duration: 0.4 }}
                        sx={{
                            display: "flex",
                            alignItems: "center",
                            gap: { xs: 0.8, sm: 1.5 },
                        }}
                    >
                        <ToggleButtonGroup
                            exclusive
                            size="small"
                            value={language}
                            onChange={(_, value: AppLanguage | null) => {
                                if (value) onLanguageChange(value);
                            }}
                            sx={{
                                height: 34,
                                bgcolor: "background.default",
                                borderRadius: 2,
                            }}
                        >
                            <ToggleButton value="en">EN</ToggleButton>
                            <ToggleButton value="id">ID</ToggleButton>
                        </ToggleButtonGroup>

                        <Button
                            variant={isInstalled || canInstall ? "contained" : "outlined"}
                            color={isInstalled ? "warning" : canInstall ? "error" : "primary"}
                            onClick={actionHandler}
                            disabled={!actionEnabled}
                            sx={{
                                px: { xs: 1.5, sm: 2.4 },
                                minWidth: { xs: 74, sm: 94 },
                                borderRadius: "999px",
                                textTransform: "none",
                                fontWeight: 700,
                            }}
                        >
                            {actionLabel}
                        </Button>

                        <IconButton
                            onClick={toggleThemeColor}
                            disabled={!mounted}
                            aria-label={copy[language].theme}
                            sx={{
                                border: "1px solid",
                                borderColor: "divider",
                                backgroundColor: "background.default",
                            }}
                        >
                            <AnimatePresence mode="wait" initial={false}>
                                {mounted && (
                                    <motion.div
                                        key={isDark ? "dark" : "light"}
                                        initial={{
                                            y: -20,
                                            opacity: 0,
                                            rotate: -90,
                                        }}
                                        animate={{
                                            y: 0,
                                            opacity: 1,
                                            rotate: 0,
                                        }}
                                        exit={{ y: 20, opacity: 0, rotate: 90 }}
                                        transition={{ duration: 0.2 }}
                                        style={{
                                            display: "flex",
                                            alignItems: "center",
                                            justifyContent: "center",
                                        }}
                                    >
                                        {isDark ? (
                                            <Moon size={16} />
                                        ) : (
                                            <Sun size={16} />
                                        )}
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </IconButton>
                    </Box>
                </Box>
                {children}
            </Container>
        </Box>
    );
}

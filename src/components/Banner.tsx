import { Box, Typography, useTheme } from "@mui/material";
import { ReactNode } from "react";
import { motion } from "motion/react";
import { BatteryCharging, Sparkles } from "lucide-react";
import type { AppLanguage } from "@/Entry";

export interface BannerProps {
    children?: ReactNode;
    title: string;
    subtitle: string;
    language: AppLanguage;
}

export default function Banner({
    children,
    title,
    subtitle,
    language,
}: BannerProps) {
    const theme = useTheme();

    const copy = {
        en: { badge: "Simple planner" },
        id: { badge: "Perencana sederhana" },
    };

    return (
        <Box
            component={motion.div}
            initial={{ opacity: 0, y: 20, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            sx={{
                position: "relative",
                overflow: "hidden",
                borderRadius: 4,
                background: `linear-gradient(120deg, ${theme.palette.primary.dark} 0%, ${theme.palette.primary.main} 52%, ${theme.palette.info.main} 100%)`,
                color: "primary.contrastText",
                // boxShadow: `0 12px 40px -12px ${theme.palette.primary.main}`,
                mb: 4,
            }}
        >
            <Box
                component={motion.div}
                animate={{
                    y: [-10, 8, -10],
                    rotate: [-5, 5, -5],
                }}
                transition={{
                    duration: 6,
                    repeat: Infinity,
                    ease: "easeInOut",
                }}
                sx={{
                    position: "absolute",
                    right: -40,
                    top: -60,
                    opacity: 0.15,
                    pointerEvents: "none",
                }}
            >
                <Sparkles size={220} />
            </Box>

            <Box
                sx={{
                    position: "relative",
                    zIndex: 1,
                    p: { xs: 3, md: 4 },
                    display: "flex",
                    flexDirection: { xs: "column", sm: "row" },
                    alignItems: { xs: "flex-start", sm: "center" },
                    gap: 3,
                }}
            >
                <Box
                    sx={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        width: 72,
                        height: 72,
                        borderRadius: 3,
                        backgroundColor: "rgba(255, 255, 255, 0.15)",
                        backdropFilter: "blur(12px)",
                        border: "1px solid rgba(255, 255, 255, 0.2)",
                        flexShrink: 0,
                    }}
                >
                    <BatteryCharging size={36} color="#ffffff" />
                </Box>

                <Box sx={{ flex: 1 }}>
                    <Typography
                        variant="overline"
                        sx={{
                            opacity: 0.9,
                            fontWeight: 800,
                            letterSpacing: ".12em",
                        }}
                    >
                        {copy[language].badge}
                    </Typography>
                    <Typography
                        variant="h1"
                        sx={{
                            fontWeight: 900,
                            fontSize: { xs: 24, md: 32 },
                            mb: 1,
                            letterSpacing: "-0.02em",
                            lineHeight: 1.2,
                        }}
                    >
                        {title}
                    </Typography>
                    <Typography
                        variant="body1"
                        sx={{
                            opacity: 0.9,
                            fontWeight: 500,
                            fontSize: { xs: 14, md: 16 },
                            maxWidth: 580,
                        }}
                    >
                        {subtitle}
                    </Typography>
                </Box>

                {children && (
                    <Box sx={{ mt: { xs: 2, sm: 0 }, ml: { sm: "auto" } }}>
                        {children}
                    </Box>
                )}
            </Box>
        </Box>
    );
}
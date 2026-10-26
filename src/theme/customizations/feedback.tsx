"use client";
import { Theme, Components, alpha } from "@mui/material/styles";
import { gray, shape } from "../themePrimitives";

/* eslint-disable import/prefer-default-export */
export const feedbackCustomizations: Components<Theme> = {
    MuiDialog: {
        styleOverrides: {
            root: ({ theme }) => ({
                "& .MuiDialog-paper": {
                    borderRadius: shape.borderRadius,
                    border: "1px solid",
                    // @ts-ignore
                    borderColor: (theme.vars || theme).palette.divider,
                },
            }),
        },
    },
    MuiLinearProgress: {
        styleOverrides: {
            root: ({ theme }) => ({
                height: 8,
                borderRadius: shape.borderRadius,
                backgroundColor: gray[200],
                ...theme.applyStyles("dark", {
                    backgroundColor: gray[800],
                }),
            }),
        },
    },
    MuiSkeleton: {
        styleOverrides: {
            root: ({ theme }) => ({
                cursor: "wait",
                background: "#0001",
                ...theme.applyStyles("dark", {
                    background: "#fff1",
                }),
            }),
        },
    },
    MuiAlert: {
        styleOverrides: {
            root: ({ theme }) => {
                return {
                    fontWeight: 500,
                    transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                    backdropFilter: "blur(10px)",
                    position: "relative",
                    "& .MuiAlertTitle-root": {
                        fontWeight: 600,
                        fontSize: 18,
                        marginTop: -4,
                    },
                    "& .MuiAlert-message": {
                        width: "100%",
                        display: "flex",
                        flexDirection: "column",
                        justifyContent: "flex-start",
                        alignItems: "flex-start",
                    },

                    ...theme.applyStyles("dark", {
                        backdropFilter: "blur(12px)",
                    }),
                };
            },
        },
    },
    MuiTooltip: {
        styleOverrides: {
            popper: {
                pointerEvents: "none",
            },
        },
    },
};

// Helper function to convert hex to rgb
function hexToRgb(hex: string): string {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result
        ? `${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}`
        : "0, 0, 0";
}

// Helper function to determine contrast text color
function getContrastText(background: string): string {
    // Simple contrast calculation - in a real implementation,
    // you might want to use theme.palette.getContrastText()
    const rgb = hexToRgb(background)
        .split(",")
        .map((val) => parseInt(val.trim()));
    const brightness = (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000;
    return brightness > 128 ? "#000000" : "#ffffff";
}

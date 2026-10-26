"use client";
import { ReactNode, useMemo } from "react";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import type { ThemeOptions } from "@mui/material/styles";
import { inputsCustomizations } from "./customizations/inputs";
import { dataDisplayCustomizations } from "./customizations/dataDisplay";
import { feedbackCustomizations } from "./customizations/feedback";
import { navigationCustomizations } from "./customizations/navigation";
import { surfacesCustomizations } from "./customizations/surfaces";
import { colorSchemes, typography, shadows, shape } from "./themePrimitives";
import figtree from "./fonts/Figtree.ttf";

const THEME_MODE_STORAGE_KEY = "theme-mode";

interface Props {
    children: ReactNode;
    themeComponents?: ThemeOptions["components"];
}

export default function Theme({ children, themeComponents }: Props) {
    const theme = useMemo(() => {
        return createTheme({
            cssVariables: {
                colorSchemeSelector: "data-color-scheme",
                cssVarPrefix: "template",
            },
            colorSchemes, 
            typography,
            shape,
            shadows: shadows.light || shadows,
            components: {
                ...inputsCustomizations,
                ...dataDisplayCustomizations,
                ...feedbackCustomizations,
                ...navigationCustomizations,
                ...surfacesCustomizations,
                ...themeComponents,
                MuiCssBaseline: {
                    styleOverrides: {
                        '@font-face': {
                            fontFamily: 'Figtree',
                            src: `url(${figtree}) format('truetype')`,
                            fontStyle: 'normal',
                            fontDisplay: 'swap',
                            fontWeight: '100 900', // Updated for variable font support
                        },
                        body: {
                            fontFamily: '"Figtree", sans-serif',
                        },
                    },
                },
            },
        });
    }, [themeComponents]);

    return (
        <ThemeProvider
            theme={theme}
            modeStorageKey={THEME_MODE_STORAGE_KEY}
            defaultMode="light"
            disableTransitionOnChange
        >
            {children}
        </ThemeProvider>
    );
}
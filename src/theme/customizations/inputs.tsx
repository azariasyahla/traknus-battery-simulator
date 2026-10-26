import { Theme, Components, alpha } from "@mui/material/styles";
import { COLOR_SCHEME, shape } from "../themePrimitives";

export const inputsCustomizations: Components<Theme> = {
    MuiTextField: {
        styleOverrides: {
            root: {
                "& .MuiInputBase-root": {
                    fontSize: "1em",
                },
                "& .MuiInputLabel-root": {
                    fontSize: "1em",
                    transform: "translate(1em, 35%) scale(1)",
                    "&[data-shrink=true]": {
                        transform: "translate(1em, -50%) scale(.75)",
                    },
                },
                "& input, .MuiSelect-select": {
                    padding: ".35em 1em",
                },
                "& .MuiSvgIcon-root": {
                    width: ".75em",
                    height: ".75em",
                    top: "calc(50% - .4em)",
                },
            },
        },

        variants: [
            {
                props: { size: "small" },
                style: { fontSize: "12px" },
            },
            {
                props: { size: "medium" },
                style: { fontSize: "14px" },
            }
        ],
    },

    MuiSelect: {
        styleOverrides: {},
    },

    MuiButton: {
        styleOverrides: {
            root: ({ theme, ownerState }) => {
                return {
                    minWidth: 0,
                    minHeight: 0,
                    padding: "4px",
                    borderRadius: "4px",
                    border: "none",
                    variants: [
                        ...COLOR_SCHEME.map((colorName) => [
                            // contained
                            {
                                props: {
                                    color: colorName,
                                    variant: "contained",
                                },
                                style: {
                                    backgroundColor:
                                        theme.palette[colorName].main,
                                    color: theme.palette.getContrastText(
                                        theme.palette[colorName].main,
                                    ),
                                    "&:hover": {
                                        backgroundColor: alpha(
                                            theme.palette[colorName].main,
                                            0.75,
                                        ),
                                        color: theme.palette.getContrastText(
                                            alpha(
                                                theme.palette[colorName].main,
                                                0.75,
                                            ),
                                        ),
                                    },

                                    ...theme.applyStyles("dark", {
                                        backgroundColor:
                                            theme.palette[colorName].main,
                                        color: theme.palette.getContrastText(
                                            theme.palette[colorName].main,
                                        ),
                                    }),
                                },
                            },

                            // outlined
                            {
                                props: {
                                    color: colorName,
                                    variant: "outlined",
                                },
                                style: {
                                    backgroundColor: alpha(
                                        theme.palette[colorName].main,
                                        0.15,
                                    ),
                                    color: theme.palette[colorName].main,
                                    border: "1px solid",
                                    borderColor: theme.palette[colorName].main,
                                    "&:hover": {
                                        backgroundColor: alpha(
                                            theme.palette[colorName].main,
                                            0.75,
                                        ),
                                        color: theme.palette.getContrastText(
                                            theme.palette[colorName].main,
                                        ),
                                    },

                                    ...theme.applyStyles("dark", {
                                        color: theme.palette[colorName].light,
                                    }),
                                },
                            },

                            {
                                props: {
                                    color: colorName,
                                    variant: "text",
                                },
                                style: {
                                    color: theme.palette.getContrastText(
                                        theme.palette[colorName].dark,
                                    ),
                                },
                            },
                        ]).flat(),
                        ...["small", "medium", "large"].map((size, i) => ({
                            props: {
                                size,
                            },
                            style: {
                                minWidth: 0,
                                minHeight: 0,
                                padding: `${2 * (i + 1)}px`,
                                fontSize: `${8 + i * 1}px`,
                            },
                        })),
                    ],
                };
            },
        },
    },

    MuiIconButton: {
        defaultProps: {
            active: false,
            outlined: false,
            component: ({ active, outlined, ref, ...props }) => {
                return <button ref={ref} {...props} />;
            },
        },
        styleOverrides: {
            root: ({ theme, ownerState }) => {
                return {
                    minWidth: 0,
                    minHeight: 0,
                    padding: "4px",
                    borderRadius: "4px",
                    variants: [
                        ...COLOR_SCHEME.map((colorName) => ({
                            props: {
                                color: colorName,
                            },
                            style: {
                                backgroundColor: alpha(
                                    theme.palette[colorName].main,
                                    0.15,
                                ),
                                color: theme.palette[colorName].main,
                                "&:hover": {
                                    backgroundColor: alpha(
                                        theme.palette[colorName].main,
                                        0.75,
                                    ),
                                    color: theme.palette.getContrastText(
                                        theme.palette[colorName].main,
                                    ),
                                },

                                ...theme.applyStyles("dark", {
                                    color: theme.palette[colorName].light,
                                }),

                                ...(ownerState.active && {
                                    backgroundColor:
                                        theme.palette[colorName].main,
                                    color: theme.palette.getContrastText(
                                        theme.palette[colorName].main,
                                    ),
                                    "&:hover": {
                                        backgroundColor: alpha(
                                            theme.palette[colorName].main,
                                            0.85,
                                        ),
                                        color: theme.palette.getContrastText(
                                            theme.palette[colorName].main,
                                        ),
                                    },
                                }),

                                ...(ownerState.outlined && {
                                    outline: "1px solid",
                                    outlineColor: alpha(
                                        theme.palette[colorName].contrastText,
                                        0.5,
                                    ),
                                }),
                            },
                        })),
                        ...["small", "medium", "large"].map((size, i) => ({
                            props: {
                                size,
                            },
                            style: {
                                minWidth: 0,
                                minHeight: 0,
                                padding: `${2 * (i + 1)}px`,
                                borderRadius: shape?.borderRadius,
                            },
                        })),
                    ],
                };
            },
        },
    },

    MuiButtonGroup: {
        styleOverrides: {
            root: ({ theme }) => ({
                overflow: "hidden",
                // outline: "1px solid",
                // outlineColor: "#9fbeec",
                borderRadius: shape.borderRadius
                    ? 0.75 * shape.borderRadius
                    : 0,
                "& .MuiButton-root": {
                    borderRadius: 0,

                    "&:first-of-type": {
                        borderTopLeftRadius: shape?.borderRadius
                            ? 0.75 * shape.borderRadius
                            : 0,
                        borderBottomLeftRadius: shape?.borderRadius
                            ? 0.75 * shape.borderRadius
                            : 0,
                    },

                    "&:last-of-type": {
                        borderTopRightRadius: shape?.borderRadius
                            ? 0.75 * shape.borderRadius
                            : 0,
                        borderBottomRightRadius: shape?.borderRadius
                            ? 0.75 * shape.borderRadius
                            : 0,
                    },
                },
            }),
        },
    },
};

import "@mui/material";

declare module "@mui/material/TextField" {
    interface TextFieldPropsSizeOverrides {
        compact: true;
    }
}

declare module "@mui/material" {
    interface IconButtonOwnProps {
        active?: boolean;
        outlined?: boolean;
        size?: "small" | "medium" | "large";
    }
}

// Image Declarations
declare module "*.png" {
    const value: string;
    export default value;
}
declare module "*.jpg" {
    const value: string;
    export default value;
}
declare module "*.jpeg" {
    const value: string;
    export default value;
}
declare module "*.svg" {
    const value: string;
    export default value;
}
declare module "*.webp" {
    const value: string;
    export default value;
}
declare module "*.gif" {
    const value: string;
    export default value;
}

// Font Declarations
declare module "*.woff" {
    const value: string;
    export default value;
}
declare module "*.woff2" {
    const value: string;
    export default value;
}
declare module "*.ttf" {
    const value: string;
    export default value;
}
declare module "*.otf" {
    const value: string;
    export default value;
}



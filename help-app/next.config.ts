import type { NextConfig } from "next";

const config: NextConfig = {
  // Help sub-app must transpile the shared TS-source package distributed
  // without a compile step.
  transpilePackages: ["@aios/help-portal"],
};

export default config;

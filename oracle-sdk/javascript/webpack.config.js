import { createRequire } from "node:module";
import webpack from "webpack";

const require = createRequire(import.meta.url);
const configs = {
  mode: "none",
  entry: {
    lightecho_stellar_oracle: [`./lightecho_stellar_oracle.js`],
  },
  output: {
    filename: `[name].min.js`,
    library: "OracleClient",
    libraryExport: "default",
    libraryTarget: "umd",
    globalObject: "this",
  },
  plugins: [
    // Work around for Buffer is undefined:
    // https://github.com/webpack/changelog-v5/issues/10
    new webpack.ProvidePlugin({
      Buffer: ["buffer", "Buffer"],
    }),
    new webpack.ProvidePlugin({
      process: "process/browser",
    }),
  ],
  resolve: {
    extensions: [".ts", ".js"],
    fallback: {
      buffer: require.resolve("buffer"),
      "process/browser": require.resolve("process/browser"),
    },
  },
};
export default configs;

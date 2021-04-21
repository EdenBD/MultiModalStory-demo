module.exports = {
  "transpileDependencies": [
    "vuetify"
  ],
  publicPath: "",
  devServer: {
    proxy: {
      "^/api": {
        target: "http://localhost:8000",
        changeOrigin: true
      }
    }
  }
}

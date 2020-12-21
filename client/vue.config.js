module.exports = {
  "transpileDependencies": [
    "vuetify"
  ],
  publicPath: "/storygen/",
  devServer: {
    proxy: {
      "^/api": {
        target: "http://localhost:8000",
        changeOrigin: true
      }
    }
  }
}

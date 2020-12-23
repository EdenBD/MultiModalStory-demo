import Vue from 'vue'
import App from './App.vue'
import Editor from './components/Editor.vue'
import vuetify from './plugins/vuetify';
import VueRouter from 'vue-router';

Vue.config.productionTip = false
Vue.use(VueRouter)

const router = new VueRouter({
  mode: 'history',
  routes: [
    { path: '/:storyid', name: 'story', component: Editor },
    {
      path: '*'
    }
  ]
})

new Vue({
  vuetify, router,
  render: h => h(App)
}).$mount('#app')
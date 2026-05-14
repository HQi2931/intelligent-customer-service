import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// Vant 按需
import 'vant/lib/index.css'
import { Button, Field, Form, Tab, Tabs, NavBar, Cell, Dialog, Toast, Popup, SwipeCell, Notify } from 'vant'

const app = createApp(App)
app.use(router)

// 注册 Vant 组件
;[Button, Field, Form, Tab, Tabs, NavBar, Cell, Dialog, Toast, Popup, SwipeCell, Notify].forEach(c => app.use(c))

app.mount('#app')
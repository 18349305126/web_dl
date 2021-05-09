import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)

/* Layout */
import Layout from '@/layout'

/**
 * Note: sub-menu only appear when route children.length >= 1
 * Detail see: https://panjiachen.github.io/vue-element-admin-site/guide/essentials/router-and-nav.html
 *
 * hidden: true                   if set true, item will not show in the sidebar(default is false)
 * alwaysShow: true               if set true, will always show the root menu
 *                                if not set alwaysShow, when item has more than one children route,
 *                                it will becomes nested mode, otherwise not show the root menu
 * redirect: noRedirect           if set noRedirect will no redirect in the breadcrumb
 * name:'router-name'             the name is used by <keep-alive> (must set!!!)
 * meta : {
    roles: ['admin','editor']    control the page roles (you can set multiple roles)
    title: 'title'               the name show in sidebar and breadcrumb (recommend set)
    icon: 'svg-name'/'el-icon-x' the icon show in the sidebar
    breadcrumb: false            if set false, the item will hidden in breadcrumb(default is true)
    activeMenu: '/example/list'  if set path, the sidebar will highlight the path you set
  }
 */

/**
 * constantRoutes
 * a base page that does not have permission requirements
 * all roles can be accessed
 */
export const constantRoutes = [
  {
    path:'/visible',
    component: ()=> import('@/views/visible/VisiblePage'),

  },
  {
    path:'/visibleshow',
    component: ()=> import('@/views/visible/VisibleShowTest'),

  },
  {
    path: '/login',
    component: () => import('@/views/login/index'),
    hidden: true
  },

  {
    path: '/404',
    component: () => import('@/views/404'),
    hidden: true
  },

  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [{
      path: 'dashboard',
      name: 'Dashboard',
      component: () => import('@/views/dashboard/index'),
      meta: { title: '首页', icon: 'dashboard' }
    }]
  },

  {
    path: '/project',
    component: Layout,
    redirect: '/project/history',
    name: 'Project',
    meta: { title: '项目', icon: 'chart' },
    children: [
      {
        path: 'create',
        component: () => import('@/views/project/list/create'),
        name: 'CreateProject',
        meta: { title: '创建项目', icon: 'edit' }
      },
      {
        path: 'edit/:id(\\d+)',
        component: () => import('@/views/project/list/edit'),
        name: 'EditProject',
        meta: { title: '编辑项目', noCache: true, activeMenu: '/project/list' },
        hidden: true
      },
      {
        path: 'list',
        name: 'ProjectList',
        component: () => import('@/views/project/list/index'),
        meta: { title: '项目列表', icon: 'tree' }
      },
      {
        path: 'board/:id(\\d+)',
        name: 'DarwingBoard',
        component: () => import('@/views/project/board/index'),
        meta: { title: '流程绘制板', noCache: true, activeMenu: 'project/list' },
        hidden: true
      },
      {
        path: 'history',
        name: 'ProjectHistory',
        component: () => import('@/views/project/history/index'),
        meta: { title: '执行记录', icon: 'skill' }
      }
    ]
  },

  {
    path: '/dataset',
    component: Layout,
    redirect: '/dataset/list',
    name: 'Dataset',
    meta: {
      title: '数据',
      icon: 'list'
    },
    children: [
      {
        path: 'create',
        component: () => import('@/views/dataset/list/create'),
        name: 'CreateDataset',
        meta: { title: '创建数据集', icon: 'edit' }
      },
      {
        path: 'edit/:id(\\d+)',
        component: () => import('@/views/dataset/list/edit'),
        name: 'EditDataset',
        meta: { title: '编辑数据集', noCache: true, activeMenu: '/dataset/list' },
        hidden: true
      },
      {
        path: 'list',
        name: 'DatasetList',
        component: () => import('@/views/dataset/list/index'),
        meta: { title: '数据集列表', icon: 'tree' }
      }
    ]
  },

  {
    path: '/form',
    component: Layout,
    children: [
      {
        path: 'index',
        name: 'Form',
        component: () => import('@/views/form/index'),
        meta: { title: 'Form', icon: 'form' }
      }
    ]
  },

  {
    path: '/external-link',
    component: Layout,
    children: [
      {
        path: 'https://panjiachen.github.io/vue-element-admin-site/#/',
        meta: { title: '外链', icon: 'link' }
      }
    ]
  },

  // 404 page must be placed at the end !!!
  { path: '*', redirect: '/404', hidden: true }
]

const createRouter = () => new Router({
  // mode: 'history', // require service support
  scrollBehavior: () => ({ y: 0 }),
  routes: constantRoutes,
  mode: 'history'
})

const router = createRouter()

// Detail see: https://github.com/vuejs/vue-router/issues/1234#issuecomment-357941465
export function resetRouter() {
  const newRouter = createRouter()
  router.matcher = newRouter.matcher // reset router
}

export default router

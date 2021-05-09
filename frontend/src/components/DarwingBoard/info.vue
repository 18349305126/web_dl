<template>
  <el-dialog
    title="流程数据信息"
    :visible.sync="dialogVisible"
    width="70%"
  >
    <el-alert
      title="使用说明"
      type="warning"
      description="以下流程信息可以被存储起来，方便下一次流程加载"
      show-icon
      close-text="知道了"
    />
    <br>
    <!--一个高亮显示的插件-->
    <codemirror
      :value="flowJsonData"
      :v-bind="options"
      class="code"
    />
  </el-dialog>
</template>

<script>
import 'codemirror/lib/codemirror.css'
import { codemirror } from 'vue-codemirror'

require('codemirror/mode/javascript/javascript.js')

export default {
  components: {
    codemirror
  },
  props: {
    data: Object
  },
  data() {
    return {
      dialogVisible: false,
      flowJsonData: {},
      options: {
        mode: { name: 'javascript', json: true },
        lineNumbers: true
      }
    }
  },
  methods: {
    init() {
      this.dialogVisible = true
      this.flowJsonData = JSON.stringify(this.data, null, 4).toString()
    }
  }
}
</script>

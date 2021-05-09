<template>
  <div>
    <el-select v-model="selectData" multiple collapse-tags placeholder="模态" class="select-item" @change="changeData">
      <el-option
        v-for="item1 in treeData"
        :key="item1.key"
        :label="item1.label"
        :value="item1.key"
      >
        <span>{{ item1.label }}</span>
        <div class="el-pot-right">
          <el-option
            v-for="item2 in item1.children"
            :key="item2.key"
            :label="item2.label"
            :value="item2.key"
          >
            <span>{{ item2.label }}</span>
          </el-option>
        </div>
      </el-option>
    </el-select>
  </div>
</template>
<script>
export default {
  name: 'MySelect',
  model: {
    prop: 'data',
    event: 'revert'
  },
  props: {
    treeData: {
      type: Array,
      default() {
        return []
      }
    }
  },
  data() {
    return {
      selectData: []
    }
  },
  methods: {
    changeData() {
      this.$emit('revert', this.selectData)
    }
  }
}
</script>
<style>
  .el-pot-right{
    position: absolute;
    top:0;
    right: -105%;
    width: 100%;
    display: none;
    background-color: #FFF;
    border: 1px solid #E4E7ED;
    box-shadow: 0 2px 12px 0 rgba(0,0,0,.1);
    box-sizing: border-box;
    border-radius: 4px;
    padding: 5px 0;
  }
  .is-multiple .el-scrollbar{
    overflow: initial;
  }
  .is-multiple .el-scrollbar__wrap{
    overflow: initial;
    margin-right:0 !important;
    margin-bottom: 0 !important;
  }
  .is-multiple .el-select-dropdown__item{
    overflow: initial;
  }
  .is-multiple .el-select-dropdown__item>.el-pot-right:hover{
    display: inline-block;
  }
  .is-multiple .el-select-dropdown__item.hover>.el-pot-right{
    display: inline-block;
  }
  .is-multiple .el-scrollbar__bar{
    display: none !important;
    opacity:0 !important;
  }

</style>

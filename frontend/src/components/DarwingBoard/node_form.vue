<template>
  <div>
    <div class="ef-node-form">
      <div class="ef-node-form-header">
        编辑
      </div>
      <div class="ef-node-form-body">
        <el-form :model="node" ref="dataForm" label-width="80px" v-show="type === 'node'">
          <el-form-item label="类型">
            <el-input
              v-model="node.type"
              :disabled="true"
            />
          </el-form-item>
          <el-form-item label="方法">
            <el-input
               v-model="node.method"
               :disabled="true"
          />
          </el-form-item>
          <el-form-item label="名称">
            <el-input v-model="node.name" />
          </el-form-item>

          <!-- transform -->

          <el-form-item
            v-if="node.method=='dcm2mhd'||node.method=='dcm2mha'||node.method=='dcm2nii'||node.method=='dcm2niigz'"
            key="1"
            label="dcm_dir"
          >
            <input
              id="file"
              type="file"
              hidden
              webkitdirectory
              @change="fileChange"
            >
            <el-input
              v-model="node.dcm_dir"
              class="input-with-select"
            >
              <el-button
                slot="append"
                icon="el-icon-folder"
                type="success"
                @click="btnChange"
              />
            </el-input>
          </el-form-item>

          <el-form-item
            v-if="node.method=='dcm2mhd'||node.method=='mhd2nii'"
            key="2"
            label="mhd_dir"
          >
            <input
              id="file"
              type="file"
              hidden
              webkitdirectory
              @change="fileChange"
            >
            <el-input
              v-model="node.mhd_dir"
              class="input-with-select"
            >
              <el-button
                slot="append"
                icon="el-icon-folder"
                type="success"
                @click="btnChange"
              />
            </el-input>
          </el-form-item>

          <el-form-item
            v-if="node.method=='dcm2mhd'||node.method=='dcm2mha'||node.method=='dcm2nii'||node.method=='dcm2niigz'"
            key="3"
            label="seg_path"
          >
            <input
              id="file"
              type="file"
              hidden
              webkitdirectory
              @change="fileChange"
            >
            <el-input
              v-model="node.seg_path"
              class="input-with-select"
            >
              <el-button
                slot="append"
                icon="el-icon-folder"
                type="success"
                @click="btnChange"
              />
            </el-input>
          </el-form-item>

          <el-form-item
            v-if="node.method=='dcm2mha'||node.method=='mha2nii'"
            key="4"
            label="mha_dir"
          >
            <input
              id="file"
              type="file"
              hidden
              webkitdirectory
              @change="fileChange"
            >
            <el-input
              v-model="node.mha_dir"
              class="input-with-select"
            >
              <el-button
                slot="append"
                icon="el-icon-folder"
                type="success"
                @click="btnChange"
              />
            </el-input>
          </el-form-item>

          <el-form-item
            v-if="node.method=='dcm2mha'||node.method=='dcm2nii'||node.method=='dcm2niigz'"
            key="5"
            label="category">
            <el-input v-model="node.category" />
          </el-form-item>

          <el-form-item
            v-if="node.method=='dcm2nii'||node.method=='mha2nii'||node.method=='mhd2nii'"
            key="6"
            label="nii_dir"
          >
            <input
              id="file"
              type="file"
              hidden
              webkitdirectory
              @change="fileChange"
            >
            <el-input
              v-model="node.nii_dir"
              class="input-with-select"
            >
              <el-button
                slot="append"
                icon="el-icon-folder"
                type="success"
                @click="btnChange"
              />
            </el-input>
          </el-form-item>

          <el-form-item
            v-if="node.method=='dcm2niigz'"
            key="8"
            label="niigz_dir"
          >
            <input
              id="file"
              type="file"
              hidden
              webkitdirectory
              @change="fileChange"
            >
            <el-input
              v-model="node.niigz_dir"
              class="input-with-select"
            >
              <el-button
                slot="append"
                icon="el-icon-folder"
                type="success"
                @click="btnChange"
              />
            </el-input>
          </el-form-item>

<!-- cut -->

          <el-form-item
            v-if="node.method=='cut'"
            key="8"
            label="data_path"
          >
            <input
              id="file"
              type="file"
              hidden
              webkitdirectory
              @change="fileChange"
            >
            <el-input
              v-model="node.data_path"
              class="input-with-select"
            >
              <el-button
                slot="append"
                icon="el-icon-folder"
                type="success"
                @click="btnChange"
              />
            </el-input>
          </el-form-item>

          <el-form-item
            v-if="node.method=='cut'"
            key="9"
            label="save_path"
          >
            <input
              id="file"
              type="file"
              hidden
              webkitdirectory
              @change="fileChange"
            >
            <el-input
              v-model="node.save_path"
              class="input-with-select"
            >
              <el-button
                slot="append"
                icon="el-icon-folder"
                type="success"
                @click="btnChange"
              />
            </el-input>
          </el-form-item>

          <el-form-item
             v-if="node.method=='cut'"
             key="10"
             label="format">
             <el-input v-model="node.format" />
          </el-form-item>

          <el-form-item
            v-if="node.method=='cut'"
            key="11"
            label="hsize">
            <el-input v-model="node.hsize" />
          </el-form-item>

          <el-form-item
             v-if="node.method=='cut'"
             key="12"
             label="wsize">
             <el-input v-model="node.wsize" />
         </el-form-item>

<!-- test -->

          <el-form-item
            v-if="node.method=='test'||node.method=='train'"
            key="13"
            label="model_path"
          >
            <input
              id="file"
              type="file"
              hidden
              webkitdirectory
              @change="fileChange"
            >
            <el-input
              v-model="node.model_path"
              class="input-with-select"
            >
              <el-button
                slot="append"
                icon="el-icon-folder"
                type="success"
                @click="btnChange"
              />
            </el-input>
          </el-form-item>

          <el-form-item
             v-if="node.method=='test'||node.method=='train'"
             key="14"
             label="model_name">
             <el-input v-model="node.model_name" />
         </el-form-item>

          <el-form-item
            v-if="node.method=='test'"
            key="15"
            label="param"
          >
            <input
              id="file"
              type="file"
              hidden
              webkitdirectory
              @change="fileChange"
            >
            <el-input
              v-model="node.param"
              class="input-with-select"
            >
              <el-button
                slot="append"
                icon="el-icon-folder"
                type="success"
                @click="btnChange"
              />
            </el-input>
          </el-form-item>

          <el-form-item
            v-if="node.method=='train'"
            key="16"
            label="param_path"
          >
            <input
              id="file"
              type="file"
              hidden
              webkitdirectory
              @change="fileChange"
            >
            <el-input
              v-model="node.param_path"
              class="input-with-select"
            >
              <el-button
                slot="append"
                icon="el-icon-folder"
                type="success"
                @click="btnChange"
              />
            </el-input>
          </el-form-item>



          <el-form-item>
            <el-button icon="el-icon-close">重置</el-button>
            <el-button
              type="primary"
              icon="el-icon-check"
              @click="save"
            >保存</el-button>
          </el-form-item>
        </el-form>

        <el-form
          v-show="type === 'line'"
          ref="dataForm"
          :model="line"
          label-width="80px"
        >
          <el-form-item label="条件">
            <el-input v-model="line.label" />
          </el-form-item>
          <el-form-item>
            <el-button icon="el-icon-close">重置</el-button>
            <el-button
              type="primary"
              icon="el-icon-check"
              @click="saveLine"
            >保存</el-button>
          </el-form-item>
        </el-form>
      </div>
      <!--            <div class="el-node-form-tag"></div>-->
    </div>
  </div>

</template>

<script>

import { cloneDeep } from 'lodash'

export default {
  data() {
    return {
      visible: true,
      // node 或 line
      type: 'node',
      node: {},
      line: {},
      data: {},
      dcm_dir: {},
      mhd_dir: {},
      seg_path: {},
      mha_dir:{},
      category:{},
      nii_dir:{},
      nii_dir:{},
      data_path:{},
      save_path:{},
      format:{},
      hsize:{},
      wsize:{},
      model_path:{},
      model_name:{},
      param:{},
      param_path:{}
    }
  },
  methods: {
    /**
     * 表单修改，这里可以根据传入的ID进行业务信息获取
     * @param data
     * @param id
     */
    nodeInit(data, id) {
      this.type = 'node'
      this.data = data
      data.nodeList.filter((node) => {
        if (node.id === id) {
          this.node = cloneDeep(node)
        }
      })
    },
    lineInit(line) {
      this.type = 'line'
      this.line = line
    },
    // 修改连线
    saveLine() {
      this.$emit('setLineLabel', this.line.from, this.line.to, this.line.label)
    },
    save() {
      this.data.nodeList.filter((node) => {
        if (node.id === this.node.id) {
          node.name = this.node.name
          node.left = this.node.left
          node.top = this.node.top
          node.ico = this.node.ico
          node.dcm_dir = this.node.dcm_dir
          node.mhd_dir = this.node.mhd_dir
          node.seg_path = this.node.seg_path
          node.mha_dir = this.node.mha_dir
          node.category = this.node.category
          node.nii_dir = this.node.nii_dir
          node.niigz_dir = this.node.niigz_dir
          node.data_path = this.node.data_path
          node.save_path = this.node.save_path
          node.format = this.node.format
          node.hsize = this.node.hsize
          node.wsize = this.node.wsize
          node.model_path = this.node.model_path
          node.model_name = this.node.model_name
          node.param = this.node.param
          node.param_path = this.node.param_path


          this.$emit('repaintEverything')
          console.log(node)
        }
      })
    },

    fileChange(e) {
      try {
        const fu = document.getElementById('file')
        if (fu == null) return
        this.node.dcm_dir = fu.files[0].path
        console.log(fu.files[0].path)
      } catch (error) {
        console.debug('choice file err:', error)
      }
    },

    btnChange() {
      var file = document.getElementById('file')

      file.click()
      console.log(file)
    }

  }
}
</script>

<style>
.el-node-form-tag {
  position: absolute;
  top: 50%;
  margin-left: -15px;
  height: 40px;
  width: 15px;
  background-color: #fbfbfb;
  border: 1px solid rgb(220, 227, 232);
  border-right: none;
  z-index: 0;
}
</style>

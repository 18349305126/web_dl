<template>
  <uploader
    ref="uploader"
    :options="options"
    :file-status-text="statusText"
    class="uploader-example"
    @file-complete="fileComplete"
    @complete="complete"
  >
    <uploader-unsupport />
    <uploader-drop>
      <p>将文件拖到此处，或</p>
      <uploader-btn>选择文件</uploader-btn>
      <uploader-btn :directory="true">选择文件夹</uploader-btn>
    </uploader-drop>
    <uploader-list />
  </uploader>
</template>

<script>
import { mergeFile } from '@/api/dataset'

export default {
  data() {
    return {
      options: {
        target: '/dev-api/dataset/chunk',
        testChunks: true,
        simultaneousUploads: 1,
        chunkSize: 5 * 1024 * 1023,
        autoStart: false
      },
      statusText: {
        success: '成功了',
        error: '出错了',
        uploading: '上传中',
        paused: '暂停中',
        waiting: '等待中'
      }
    }
  },
  mounted() {
    this.$nextTick(() => {
      window.uploader = this.$refs.uploader.uploader
    })
  },
  methods: {
    // 上传完成
    complete() {
      console.log('complete', arguments)
    },
    // 一个根文件（文件夹）成功上传完成。
    fileComplete() {
      console.log('file complete', arguments)
      if (!arguments[0].isFolder) {
        const file = arguments[0].file
        mergeFile({
          filename: file.name,
          identifier: arguments[0].uniqueIdentifier,
          totalSize: file.size,
          type: file.type
        }).then(function(response) {
          console.log(response)
        }).catch(function(error) {
          console.log(error)
        })
      } else {
        const files = arguments[0].files
        for (const file of files) {
          mergeFile({
            filename: file.name,
            identifier: file.uniqueIdentifier,
            totalSize: file.size,
            type: file.type
          }).then(function(response) {
            console.log(response)
          }).catch(function(error) {
            console.log(error)
          })
        }
      }
    }
  }
}
</script>

<style>
  .uploader-example {
    width: 1000px;
    padding: 15px;
    margin: 40px auto 0;
    font-size: 12px;
    box-shadow: 0 0 10px rgba(62, 146, 203, 0.4);
  }
  .uploader-example .uploader-btn {
    margin-right: 4px;
  }
  .uploader-example .uploader-list {
    max-height: 440px;
    overflow: auto;
    overflow-x: hidden;
    overflow-y: auto;
  }
</style>

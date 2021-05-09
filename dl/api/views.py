from django.views.decorators.csrf import csrf_exempt

from api.common.Result import Result
from api.services import TransformService
from api.common.logger import logger


@csrf_exempt
def transform(request):
    try:
        body = Result.parse_request_params(request)
        print(body)
        method = body['method']
        params = body['params']
    except KeyError:
        logger.warning("request contains invalid parameters")
        return Result.response_invalid()
    except Exception as e:
        logger.warning(str(e))

    success = False
    if method == 'dcm2mhd':
        dcm_dir = params['dcm_dir']
        mhd_dir = params['mhd_dir']
        seg_path = params['seg_path']
        category = ['Parotid_R', 'Parotid_L', 'Submandibular_L', 'Sunmandibular_R','OralCavity']
        success, filename = TransformService.dcm2mhd(dcm_dir, mhd_dir,seg_path,category)
    else:
        if method == 'dcm2nii':
            dcm_dir = params['dcm_dir']
            nii_dir = params['nii_dir']
            seg_path = params['seg_path']
            category = params['category']
            success, filename = TransformService.dcm2nii(dcm_dir, nii_dir, seg_path, category)
        else:
            if method == 'dcm2niigz':
                dcm_dir = params['dcm_dir']
                niigz_dir = params['niigz_dir']
                seg_path = params['seg_path']
                category = params['category']
                success, filename = TransformService.dcm2niigz(dcm_dir, niigz_dir, seg_path, category)
            else:
                if method == 'dcm2mha':
                    dcm_dir = params['dcm_dir']
                    mha_dir = params['mha_dir']
                    seg_path = params['seg_path']
                    category = params['category']
                    success, filename = TransformService.dcm2mha(dcm_dir, mha_dir, seg_path, category)
                else:
                    if method == 'mha2nii':
                        mha_dir = params['mha_dir']
                        nii_dir = params['nii_dir']
                        success, filename = TransformService.mha2nii(mha_dir, nii_dir)
                    else:
                        if method == 'mhd2nii':
                            mhd_dir = params['mhd_dir']
                            nii_dir = params['nii_dir']
                            success, filename = TransformService.mhd2nii(mhd_dir, nii_dir)


    if success:
        data = {'filename': filename}
        print(Result.response_success(data))
        return Result.response_success(data)
    # failed task
    return Result.response_fail()

@csrf_exempt
def cut(request):
    try:
        body = Result.parse_request_params(request)
        method = body['method']
        params = body['params']
    except KeyError:
        logger.warning("request contains invalid parameters")
        return Result.response_invalid()
    except Exception as e:
        logger.warning(str(e))

    success = False
    if method == 'cut':
        #data_path, save_path, format, hsize, wsize
        data_path = params['data_path']
        save_path = params['save_path']
        format = params['format']
        hsize = int(params['hsize'])
        wsize = int(params['wsize'])
        success = TransformService.cut(data_path, save_path, format, hsize, wsize)

    if success:
        data = True
        return Result.response_success(data)
    # failed task
    return Result.response_fail()

@csrf_exempt
def model(request):
    try:
        body = Result.parse_request_params(request)
        method = body['method']
        params = body['params']
    except KeyError:
        logger.warning("request contains invalid parameters")
        return Result.response_invalid()
    except Exception as e:
        logger.warning(str(e))

    success = False
    if method == 'train':
        #model_path, model_name, param_path
        model_path = params['model_path']
        model_name = params['model_name']
        param_path = params['param_path']
        success = TransformService.train(model_path, model_name, param_path)
    else:
        if method == 'test':
            # model_path, model_name, param
            model_path = params['model_path']
            model_name = params['model_name']
            param = params['param']
            success = TransformService.test(model_path, model_name, param)

    if success:
        data = True
        return Result.response_success(data)
    # failed task
    return Result.response_fail()

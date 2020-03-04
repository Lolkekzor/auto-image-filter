#include <opencv2/opencv.hpp>
#include <cmath>

using namespace cv;

#define ERR_NO_IMAGE 1
#define ERR_NON_3_CHANNEL_INPUT 2
#define ERR_WRONG_ARGS 3
#define ERR_ZERO_DIVISION 4

int srs(const Mat reflectance, const Mat &luminance, Mat &output) {
    /*
     * Strectch the pixels whose illuminance is brighter than the mean illuminance
    */
    float sum = 0;
    for(int i = 0; i < luminance.rows; i++)
    {
        const float* Mi = luminance.ptr<float>(i);
        for(int j = 0; j < luminance.cols; j++) {
            sum += Mi[j];
        }
    }

    if (sum == 0 || luminance.rows == 0 || luminance.cols == 0) return ERR_ZERO_DIVISION;
    float avg = sum / (luminance.rows * luminance.cols);

    Mat scaled = Mat(reflectance.rows, reflectance.cols, CV_32F);
    for(int i = 0; i < reflectance.rows; i++) {
        const float* reflectanceRow = reflectance.ptr<float>(i);
        const float* luminanceRow = luminance.ptr<float>(i);
        float* scaledRow = scaled.ptr<float>(i);
        for(int j = 0; j < reflectance.cols; j++) {
            scaledRow[j] = reflectanceRow[j] > avg ? reflectanceRow[j] * sqrt(luminanceRow[j] / avg) : scaledRow[j] = reflectanceRow[j];
        }
    }

    output = scaled;

    return 0;
}

int vig(const Mat &grayscale, std::vector<Mat> &resultImages)
{
    /*
     * Generates 5 different levels of illuminance for the image
     * to substitute the images taken with different exposure for
     * the HDR processing
    */
    int rows = grayscale.rows;
    int cols = grayscale.cols;
    Mat illuminanceImage = Mat::zeros(rows, cols, CV_32F);
    Mat invIlluminanceImage = Mat::zeros(rows, cols, CV_32F);
    float maxInvIlluminance = 0.0f;
    float meanIlluminance = 0.0f;
    float maxIlluminance = 0.0f;
    for(int row = 0; row < rows; row++) {
        for(int col = 0; col < cols; col++) {
            float illuminanceValue = grayscale.at<float>(row, col);
            illuminanceImage.at<float>(row, col) = illuminanceValue;
            invIlluminanceImage.at<float>(row, col) = 1.0f - illuminanceValue;
            maxInvIlluminance = std::max(maxInvIlluminance, invIlluminanceImage.at<float>(row, col));
            meanIlluminance += illuminanceValue;
            maxIlluminance = std::max(maxIlluminance, illuminanceValue);
        }
    }

    // Normalize the inverse illuminance
    if (rows == 0  || cols == 0) return ERR_ZERO_DIVISION;
    meanIlluminance /= rows * cols;
    for(int row = 0; row < rows; row++) {
        for(int col = 0; col < cols; col++) {
            invIlluminanceImage.at<float>(row, col) = invIlluminanceImage.at<float>(row, col) / maxInvIlluminance;
        }
    }

    std::vector<float>illuminanceFactors{0.2f, 0.0f, meanIlluminance, 0.0f, 0.8f};
    illuminanceFactors[1] = (illuminanceFactors[0] + illuminanceFactors[2]) / 2.0f;
    illuminanceFactors[3] = (illuminanceFactors[2] + illuminanceFactors[4]) / 2.0f;
    float r = 1.0f - meanIlluminance / maxIlluminance;
    for(auto &illuminance : illuminanceFactors) {
        illuminance = (r * (1.0f / (1 + exp(-1.0f * (illuminance - meanIlluminance))) - 0.5f));
    }

    std::vector<Mat> vigImages;
    for(auto illuminance : illuminanceFactors) {
        Mat currentVig = Mat::zeros(rows, cols, CV_32F);
        float illuminanceTmp = 1.0f + illuminance;
        for(int row = 0; row < rows; row++) {
            for(int col = 0; col < cols; col++) {
                currentVig.at<float>(row, col) = illuminanceTmp * 
                        (illuminanceImage.at<float>(row, col) + illuminance * invIlluminanceImage.at<float>(row, col));
            }
        }
        vigImages.push_back(currentVig);
    }
    resultImages = vigImages;

    return 0;
}

int tonemap(Mat &image, 
            const Mat &luminance,
            const Mat &reflectance,
            const std::vector<Mat> &generatedIlluminances,
            Mat &resultMat) {
    /*
     * Fusions the multiple exposure images to obtain the hdr image
    */
    std::vector<Mat> reflectanceLuminances, scaledLuminances;

    luminance += 1e-22;

    Mat expReflectance;
    cv::exp(reflectance, expReflectance);
    for (auto it: generatedIlluminances) {
        Mat aux = expReflectance.mul(it);
        reflectanceLuminances.push_back(aux);
    }

    image.convertTo(image, CV_32F, 1/255.0);
    std::vector<Mat> bgr(3); // Split to BGR channels {0: blue, 1: green, 2: red}
    split(image, bgr);

    int idx = 0;
    for (auto it: generatedIlluminances) {
        Mat aux;

        if (idx < 3) {
            float max;
            for(int i = 0; i < it.rows; i++) { // calculate maximum
                const float* Mi = it.ptr<float>(i);
                for(int j = 0; j < it.cols; j++)
                    max = max > Mi[j] ? max : Mi[j];
            }
            aux = it / max;
        } else {
            Mat temp = 0.5 * (-it + 1);
            float max;
            for(int i = 0; i < temp.rows; i++) { // calculate maximum
                const float* Mi = temp.ptr<float>(i);
                for(int j = 0; j < temp.cols; j++)
                    max = max > Mi[j] ? max : Mi[j];
            }
            aux = temp / max;
        }

        scaledLuminances.push_back(aux);
        idx++;
    }

    Mat A, B;
    A = reflectanceLuminances[0].mul(scaledLuminances[0]);
    B = scaledLuminances[0];
    for (int i = 1 ; i < 5 ; i++) {
        A += reflectanceLuminances[i].mul(scaledLuminances[i]);
        B += scaledLuminances[i];
    }

    Mat dividedMatrix = (A / B) / luminance;

    for(int i = 0; i < dividedMatrix.rows; i++){
        float* Mi = dividedMatrix.ptr<float>(i);
        for(int j = 0; j < dividedMatrix.cols; j++)
            Mi[j] = Mi[j] > 0 ? (Mi[j] < 3 ? Mi[j] : 3) : 0; // Clip values to range [0, 3]
    }

    bgr[0] = dividedMatrix.mul(bgr[0]);
    bgr[1] = dividedMatrix.mul(bgr[1]);
    bgr[2] = dividedMatrix.mul(bgr[2]);

    for(int i = 0; i < bgr[0].rows; i++){
        float* Mi0 = bgr[0].ptr<float>(i);
        float* Mi1 = bgr[1].ptr<float>(i);
        float* Mi2 = bgr[2].ptr<float>(i);
        for(int j = 0; j < bgr[0].cols; j++) {
            Mi0[j] = Mi0[j] > 0 ? (Mi0[j] < 1 ? Mi0[j] : 1) : 0; // Clip values to range [0, 1]
            Mi1[j] = Mi1[j] > 0 ? (Mi1[j] < 1 ? Mi1[j] : 1) : 0; // Clip values to range [0, 1]
            Mi2[j] = Mi2[j] > 0 ? (Mi2[j] < 1 ? Mi2[j] : 1) : 0; // Clip values to range [0, 1]
        }
    }

    Mat result;
    merge(bgr, result); // Merges the 3 channels in result

    resultMat = result;
    return 0;
}

int main(int argc, char** argv )
{
    int returnStatus;
    if ( argc != 3 ) {
        std::cout << "Usage: " << argv[0] << "<source_image> <dest_path>\n";
        return ERR_WRONG_ARGS;
    }

    Mat image;
    image = imread( argv[1], 1 );

    if ( !image.data ) {
        return ERR_NO_IMAGE;
    }

    Mat grayscale;
    cvtColor(image, grayscale, COLOR_BGR2GRAY);
    grayscale.convertTo(grayscale, CV_32F, 1/255.0); // grayscale /= 255.0; Luminance of the photo

    Mat filtered;
    bilateralFilter(grayscale * 255.0, filtered, 25, 30, 100);
    filtered /= 255.0;

    Mat reflectance; // Log(luminance) - Log(filter)
    Mat logLuminance, logFilter;
    cv::log((grayscale + 1e-22), logLuminance);
    cv::log((filtered + 1e-22), logFilter);
    reflectance = logLuminance - logFilter;

    Mat selfScaledReflectance;
    returnStatus = srs(reflectance, grayscale, selfScaledReflectance);
    if(returnStatus != 0) {
        return returnStatus;
    }

    std::vector<Mat> virtualLuminances;
    returnStatus = vig(grayscale, virtualLuminances);
    if(returnStatus != 0) {
        return returnStatus;
    }

    Mat result;
    returnStatus = tonemap(image, grayscale, reflectance, virtualLuminances, result);
    if(returnStatus != 0) {
        return returnStatus;
    }

    result.convertTo(result, CV_8UC3, 255);
    imwrite(argv[2], result);

    return 0;
}

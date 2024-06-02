// dependencies
import { S3Client, GetObjectCommand, PutObjectCommand } from '@aws-sdk/client-s3';

import { Readable } from 'stream';

import sharp from 'sharp';
import util from 'util';

// create S3 client
const s3 = new S3Client({ region: 'us-east-1' });

// define the handler function
export const handler = async (event, context) => {
  console.log("Reading options from event:\n", util.inspect(event, { depth: 5 }));
  const srcBucket = event.detail.bucket.name;
  const srcKey = event.detail.object.key;
  const dstBucket = `${srcBucket}-thumbnails`;
  const dstKey = `thumbnails-${srcKey}`;

  console.log("Src", srcBucket, srcKey);
  console.log("Dst", dstBucket, dstKey);

  // Infer the image type from the file suffix
  const typeMatch = srcKey.match(/\.([^.]*)$/);
  if (!typeMatch) {
    console.log("Could not determine the image type.");
    return;
  }

  // Check that the image type is supported
  const imageType = typeMatch[1].toLowerCase();
  if (imageType !== "jpg" && imageType !== "png" && imageType !== "jpeg") {
    console.log(`Unsupported image type: ${imageType}`);
    return;
  }

  // Get the image from the source bucket. GetObjectCommand returns a stream.
  try {
    const params = {
      Bucket: srcBucket,
      Key: srcKey
    };
    const response = await s3.send(new GetObjectCommand(params));
    const stream = response.Body;

    // Convert stream to buffer to pass to sharp resize function.
    if (stream instanceof Readable) {
      const content_buffer = Buffer.concat(await stream.toArray());

      // set thumbnail width. Resize will set the height automatically to maintain aspect ratio.
      const width = 200;

      // Use the sharp module to resize the image and save in a buffer.
      try {
        const output_buffer = await sharp(content_buffer).resize(width).jpeg({ quality: 70 }).toBuffer();

        // Upload the thumbnail image to the destination bucket
        try {
          const destparams = {
            Bucket: dstBucket,
            Key: dstKey,
            Body: output_buffer,
            ContentType: "image"
          };

          const putResult = await s3.send(new PutObjectCommand(destparams));
          console.log('Successfully resized ' + srcBucket + '/' + srcKey +
            ' and uploaded to ' + dstBucket + '/' + dstKey);
        } catch (error) {
          console.log(error);
          return;
        }
      } catch (error) {
        console.log(error);
        return;
      }
    } else {
      throw new Error('Unknown object stream type');
    }
  } catch (error) {
    console.log(error);
    return;
  }
};

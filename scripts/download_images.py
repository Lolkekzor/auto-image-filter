# Dear reader,
# The quality of the code in this script is not representative of what we do at Sector Labs.
# this is not an example of good code. Please don't jduge :((
#
#
# You need Python 3.5 or newer to run this :)
#
# pip3 install psycopg2
#
# $ python3 download-property-images.py [property id] [directory]

import os
import sys
import urllib.request

import psycopg2

from urllib.parse import urljoin


MEDIA_URL = "https://bayut-development.s3.amazonaws.com"
DATABASE_URL = "postgres://readonly:p5b6559e74d7c7576728141a2e29cc561046c8fe0507207406a892dfc21265d13@ec2-99-80-209-106.eu-west-1.compute.amazonaws.com:5432/d2ouuuhbqiggts"
DATABASE = psycopg2.connect(DATABASE_URL)


def _get_ad_images(ad_external_id: int):
    with DATABASE.cursor() as cursor:
        cursor.execute(
            """
                SELECT
                    image.id,
                    COALESCE(NULLIF(image.image, ''), existing_image.image)
                FROM
                    classifieds_image image
                LEFT JOIN
                    classifieds_adphoto photo
                ON
                    photo.image_id = image.id
                LEFT JOIN
                    classifieds_ad ad
                ON
                    ad.id = photo.ad_id
                LEFT JOIN
                    classifieds_image existing_image
                ON
                    existing_image.id = image.existing_image_id
                WHERE
                    ad.external_id = %s AND
                    photo.is_active = true
            """,
            (ad_external_id,),
        )

        return cursor.fetchall()


def main():
    if len(sys.argv) < 3:
        print(
            "usage: python download-property-images.py [ad external id] [destination directory]"
        )
        return 1

    ad_external_id = sys.argv[1]
    destination_directory = sys.argv[2]

    ad_images = _get_ad_images(ad_external_id)
    for image_id, image_path in ad_images:
        if not image_path:
            continue

        image_url = urljoin(MEDIA_URL, image_path)
        file_path = os.path.join(destination_directory, f"{image_id}-original.jpg")

        print(f"* Downloading {image_url} to {file_path}")
        urllib.request.urlretrieve(image_url, file_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())

import unittest

import numpy as np

from chainer import cuda
from chainer import testing
from chainer.testing import attr

from chainercv.links.model.faster_rcnn import ProposalCreator
from chainercv.utils import generate_random_bbox


@testing.parameterize(
    *testing.product({
        'test': [True, False],
    })
)
class TestProposalCreator(unittest.TestCase):

    img_size = (320, 240)
    n_anchor_base = 9
    n_train_post_nms = 350
    n_test_post_nms = 300

    def setUp(self):
        feat_size = (self.img_size[0] // 16, self.img_size[1] // 16)
        n_anchor = np.int32(self.n_anchor_base * np.prod(feat_size))

        self.score = np.random.uniform(
            low=0, high=1, size=(n_anchor,)).astype(np.float32)
        self.bbox_d = np.random.uniform(
            low=-1, high=1., size=(n_anchor, 4)).astype(np.float32)
        self.anchor = generate_random_bbox(n_anchor, self.img_size, 16, 200)
        self.proposal_creator = ProposalCreator(
            n_train_post_nms=self.n_train_post_nms,
            n_test_post_nms=self.n_test_post_nms,
            min_size=0)

    def check_proposal_creator(
            self, proposal_creator,
            bbox_d, score, anchor, img_size,
            scale=1., test=False):
        roi = self.proposal_creator(
            bbox_d, score, anchor, img_size, scale, test)

        out_length = self.n_test_post_nms \
            if test else self.n_train_post_nms
        self.assertIsInstance(roi, type(bbox_d))
        self.assertEqual(roi.shape, (out_length, 4))

    def test_proposal_creator_cpu(self):
        self.check_proposal_creator(
            self.proposal_creator,
            self.bbox_d,
            self.score,
            self.anchor, self.img_size, scale=1., test=self.test)

    @attr.gpu
    def test_proposal_creator_gpu(self):
        self.check_proposal_creator(
            self.proposal_creator,
            cuda.to_gpu(self.bbox_d),
            cuda.to_gpu(self.score),
            cuda.to_gpu(self.anchor), self.img_size,
            scale=1., test=self.test)


testing.run_module(__name__, __file__)

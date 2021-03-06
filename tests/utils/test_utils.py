import logging
import os
import unittest
import yaml
from ISR.utils import utils
from unittest.mock import patch


class UtilsClassTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logging.disable(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_config_from_weights_valid(self):
        weights = os.path.join('a', 'path', 'to', 'rdn-C3-D1-G7-G05-x2')
        arch_params = {'C': None, 'D': None, 'G': None, 'G0': None, 'x': None}
        expected_params = {'C': 3, 'D': 1, 'G': 7, 'G0': 5, 'x': 2}
        name = 'rdn'
        generated_param = utils.get_config_from_weights(
            w_path=weights, arch_params=arch_params, name=name
        )
        for p in expected_params:
            self.assertTrue(generated_param[p] == expected_params[p])

    def test_config_from_weights_invalid(self):
        weights = os.path.join('a', 'path', 'to', 'rrdn-C3-D1-G7-G05-x2')
        arch_params = {'C': None, 'D': None, 'G': None, 'G0': None, 'x': None, 'T': None}
        name = 'rdn'
        try:
            generated_param = utils.get_config_from_weights(
                w_path=weights, arch_params=arch_params, name=name
            )
        except:
            self.assertTrue(True)
        else:
            self.assertFalse(True)

    def test_setup_default_training(self):
        base_conf = {}
        base_conf['default'] = {
            'generator': 'rrdn',
            'feat_ext': False,
            'discriminator': False,
            'training_set': 'div2k-x4',
            'test_set': 'dummy',
        }
        training = True
        prediction = False
        default = True

        with patch('yaml.load', return_value=base_conf) as import_module:
            session_type, generator, conf, dataset = utils.setup(
                'tests/data/config.yml', default, training, prediction
            )
        self.assertTrue(session_type == 'training')
        self.assertTrue(generator == 'rrdn')
        self.assertTrue(conf == base_conf)
        self.assertTrue(dataset == 'div2k-x4')

    def test_setup_default_prediction(self):
        base_conf = {}
        base_conf['default'] = {
            'generator': 'rdn',
            'feat_ext': False,
            'discriminator': False,
            'training_set': 'div2k-x4',
            'test_set': 'dummy',
        }
        base_conf['generators'] = {'rdn': {'C': None, 'D': None, 'G': None, 'G0': None, 'x': None}}
        base_conf['weights_paths'] = {
            'generator': os.path.join('a', 'path', 'to', 'rdn-C3-D1-G7-G05-x2')
        }
        training = False
        prediction = True
        default = True

        with patch('yaml.load', return_value=base_conf):
            session_type, generator, conf, dataset = utils.setup(
                'tests/data/config.yml', default, training, prediction
            )
        self.assertTrue(session_type == 'prediction')
        self.assertTrue(generator == 'rdn')
        self.assertTrue(conf == base_conf)
        self.assertTrue(dataset == 'dummy')

    def test__get_parser(self):
        parser = utils._get_parser()
        cl_args = parser.parse_args(['--training'])
        namespace = cl_args._get_kwargs()
        self.assertTrue(('training', True) in namespace)
        self.assertTrue(('prediction', False) in namespace)
        self.assertTrue(('default', False) in namespace)
        pass

    @patch('builtins.input', return_value='1')
    def test_select_option(self, input):
        self.assertEqual(utils.select_option(['0', '1'], ''), '1')
        self.assertNotEqual(utils.select_option(['0', '1'], ''), '0')

    @patch('builtins.input', return_value='1')
    def test_select_positive(self, input):
        self.assertEqual(utils.select_positive(''), 1)
        self.assertNotEqual(utils.select_positive(''), 0)

    @patch('builtins.input', return_value='0')
    def test_browse_weights(self, sel_pos):
        def folder_weights_select(inp):
            if inp == '':
                return ['folder']
            if inp == 'folder':
                return ['1.hdf5']

        with patch('os.listdir', side_effect=folder_weights_select):
            weights = utils.browse_weights('')
        self.assertEqual(weights, 'folder/1.hdf5')

    @patch('builtins.input', return_value='0')
    def test_select_dataset(self, sel_opt):
        conf = yaml.load(open(os.path.join('tests', 'data', 'config.yml'), 'r'))
        conf['test_sets'] = {'test_test_set': {}}
        conf['training_sets'] = {'test_train_set': {}}

        tr_data = utils.select_dataset('training', conf)
        pr_data = utils.select_dataset('prediction', conf)

        self.assertEqual(tr_data, 'test_train_set')
        self.assertEqual(pr_data, 'test_test_set')

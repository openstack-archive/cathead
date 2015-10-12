=======
Cathead
=======

Cathead is a utility to monitor SSL certificates for expiry and retrieve new
certificates when expiry is near.

This project is borne out of frustration with using cron and certmonger and
various other bits of bash to monitor and renew certificates.

.. WARNING::
This project is under active development so expect changes to APIs and
configurations.

Running
"""""""
1. Clone repo ::

   git clone https://github.com/takac/cathead

2. Install requirements and cathead into a virtual env. ::

   virtualenv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install .

3. Construct a config file specifying which certs to track and how to refresh
   them. See the `example_config.py <example_config.py>`_ file.

   The *certs* section contains the details of the certificates to monitor and
   which driver should be used. The common name and other cert details should
   also be specified here.

   driver
     Name of the driver to use. Use the name value from the driver.

   key
     Path to the key. This key will be regenerated at every refresh.

   cert
     Path to the cert.

   common_name
     Common name of the certificate.

   on_refresh_success
     Callback action to execute on successful refresh of cert. Use the name
     value of an action defined in the actions section.

   on_refresh_failure
     Callback action to execute on failure to refresh the cert. Use the name
     value of an action defined in the actions section.

   The *drivers* section specifies how new certs are obtained, the only 2
   drivers currently supported are Anchor (currently named ECA, due to be
   changed), and self signed certs.

   name
     Name of the driver used to associate with certificates.

   driver
     Python class of the driver. e.g. ``cathead.drivers.selfsign.SelfSignDriver``.

   All other keys in the driver are passed into the driver class at
   construction. e.g. ``SelfSignDriver(**drivers['selfsign'])``

   The *actions* section contains actions to perform on different events. So
   far the possible events are

   - Successful refresh of a certificate
   - Failure to refresh a certificate

   Actions can either by system calls or python calls.

   name
     Name of the action, used to associate with a certificate event callback.

   type
      The type of action, either ``'system'`` for a system call (e.g. ``reboot``)
      or ``'python'`` which allows executing a python callable.

   module
      Use this when using type of ``python`` to select which module the
      callable is in.

   command
      Specify the command or callable to be run.

   args
      Specify the arguments to the command or callable. This should be a list.

4. Run cathead with your requirements file. ::

    cathead example_config.py

.. NOTE::
For the self signing driver you will need to generate a key to sign the certs
with. This can be done using ::

    openssl genrsa 2048 > ca.key

Known Issues
"""""""""""

Ctrl-C doesn't work

  Currently you cannot interrupt the cathead process due running the process
  from the APScheduler thread. When you run ``cathead config.py`` in the
  terminal you have to terminate the process with ``Ctrl-z`` and ``kill %1``.

Naming
""""""

The name comes from the `anchor support
<https://en.wikipedia.org/wiki/Cathead>`_ as this project can be used in
conjunction with `Anchor <https://github.com/openstack/anchor/>`_ an an
ephemeral PKI service.
